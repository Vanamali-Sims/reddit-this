"""Draft generation endpoints."""

import logging
from typing import Optional

import aiohttp
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from core.config import settings
from core.redis import rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter()


class DraftRequest(BaseModel):
    """Draft generation request model."""

    text: str = Field(..., min_length=10, max_length=1000, description="User's worry or issue")
    region: Optional[str] = Field(
        default=None, description="User's region/country for context (e.g., 'Australia')"
    )


class DraftResponse(BaseModel):
    """Draft response model."""

    title: str
    body: str
    generated_by: str
    reddit_submit_url: Optional[str] = None


@router.post("/draft", response_model=DraftResponse)
async def generate_draft(request: DraftRequest, http_request: Request):
    """
    Generate a Reddit post draft based on user's worry/issue.

    If OpenRouter API key is configured, uses LLM generation.
    Otherwise, returns a structured template.
    """
    # Rate limiting
    client_ip = http_request.client.host
    if not await rate_limiter.is_allowed(
        key=f"draft:{client_ip}",
        limit=settings.RATE_LIMIT_REQUESTS_PER_MINUTE // 2,  # More restrictive for LLM calls
        window_seconds=60,
    ):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    try:
        logger.info(f"Generating draft for: '{request.text[:50]}...'")

        if settings.OPENROUTER_API_KEY:
            # Use LLM generation
            draft = await _generate_llm_draft(request.text, request.region)
        else:
            # Use template generation
            draft = _generate_template_draft(request.text, request.region)

        return draft

    except Exception as e:
        logger.error(f"Draft generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Draft generation failed. Please try again.",
        ) from e


async def _generate_llm_draft(text: str, region: Optional[str]) -> DraftResponse:
    """Generate draft using OpenRouter LLM."""
    region_context = f" I'm in {region}." if region else ""
    
    prompt = f"""Create a Reddit post for someone experiencing this issue: "{text}"{region_context}

Generate:
1. A concise title (70-90 characters) that clearly describes the issue
2. A structured post body with:
   - Brief description of the problem
   - What they've tried (if mentioned)
   - Specific questions for the community
   - Bullet points for clarity
   - End with one clear question

Keep it authentic, respectful, and suitable for hair/skincare communities. Avoid medical advice requests.

Format as JSON:
{{"title": "...", "body": "..."}}"""

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": settings.APP_BASE_URL,
                "X-Title": "Reddit Worry Finder",
            }

            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates well-structured Reddit posts for hair and skincare communities.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 500,
                "temperature": 0.7,
            }

            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse JSON response
                    try:
                        import json
                        draft_data = json.loads(content)
                        title = draft_data.get("title", "Need advice on my hair/skin issue")
                        body = draft_data.get("body", content)
                    except json.JSONDecodeError:
                        # Fallback if not proper JSON
                        lines = content.split('\n')
                        title = lines[0] if lines else "Need advice on my hair/skin issue"
                        body = '\n'.join(lines[1:]) if len(lines) > 1 else content

                    return DraftResponse(
                        title=title[:90],  # Ensure title length limit
                        body=body,
                        generated_by="llm",
                        reddit_submit_url=f"https://www.reddit.com/submit?title={title[:90]}&text={body[:5000]}",
                    )
                else:
                    logger.warning(f"OpenRouter API error: {response.status}")
                    # Fallback to template
                    return _generate_template_draft(text, region)

    except Exception as e:
        logger.warning(f"LLM generation failed, using template: {e}")
        return _generate_template_draft(text, region)


def _generate_template_draft(text: str, region: Optional[str]) -> DraftResponse:
    """Generate draft using template."""
    # Extract key elements
    text_lower = text.lower()
    
    # Determine issue type
    if any(word in text_lower for word in ["flake", "dandruff", "itchy"]):
        issue_type = "scalp irritation"
    elif any(word in text_lower for word in ["loss", "thin", "bald"]):
        issue_type = "hair loss"
    elif any(word in text_lower for word in ["dry", "damaged", "breakage"]):
        issue_type = "hair damage"
    elif any(word in text_lower for word in ["oily", "greasy"]):
        issue_type = "oily hair"
    else:
        issue_type = "hair/scalp concern"

    # Create region context
    region_text = f" (in {region})" if region else ""

    # Generate title
    title = f"Seeking advice for {issue_type}{region_text}"

    # Generate body
    body = f"""Hi everyone,

I'm dealing with {issue_type.replace('_', ' ')} and would appreciate some advice from the community.

**My situation:**
{text}

**What I'm looking for:**
• Product recommendations that have worked for others
• Routine suggestions or changes I should consider
• Any insights into what might be causing this issue

**Questions:**
• Has anyone experienced something similar?
• What products or treatments have you found most effective?
• Are there any ingredients I should look for or avoid?

{f"I'm located in {region}, so local product availability would be helpful to know." if region else ""}

Thanks in advance for any help or advice you can share!"""

    reddit_url = f"https://www.reddit.com/submit?title={title}&text={body[:5000]}"

    return DraftResponse(
        title=title,
        body=body,
        generated_by="template",
        reddit_submit_url=reddit_url,
    )
