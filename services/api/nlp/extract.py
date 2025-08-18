"""
Text extraction and processing utilities.
"""

import logging
import re
from typing import Dict, List, Set

import yake
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

# Brand and product mappings
BRAND_MAPPINGS = {
    "nizoral": ["ketoconazole", "anti-dandruff"],
    "head and shoulders": ["h&s", "zinc pyrithione", "dandruff shampoo"],
    "selsun": ["selenium sulfide", "anti-dandruff"],
    "t gel": ["coal tar", "neutrogena"],
    "cerave": ["ceramides", "gentle cleanser"],
    "cetaphil": ["gentle cleanser", "sensitive skin"],
    "la roche posay": ["lrp", "thermal water", "sensitive skin"],
    "eucerin": ["urea", "sensitive skin"],
}

# Common synonyms for hair/scalp issues
SYNONYM_MAPPINGS = {
    "flaky": ["dandruff", "dry scalp", "seborrheic dermatitis"],
    "itchy": ["irritated", "inflamed", "sensitive"],
    "oily": ["greasy", "sebaceous", "excess oil"],
    "dry": ["dehydrated", "moisture barrier", "hydration"],
    "thinning": ["hair loss", "androgenetic alopecia", "miniaturization"],
    "damaged": ["breakage", "split ends", "protein loss"],
    "frizzy": ["humidity", "curl pattern", "moisture"],
    "color treated": ["chemically processed", "bleached", "highlighted"],
}

# Location-specific terms
LOCATION_MAPPINGS = {
    "australia": ["au", "aussie", "australian", "down under"],
    "chemist warehouse": ["cw", "pharmacy"],
    "priceline": ["australian pharmacy"],
    "woolworths": ["woolies", "supermarket"],
    "coles": ["supermarket"],
}


class TextExtractor:
    """Extract and process key information from user text."""

    def __init__(self):
        self.yake_extractor = yake.KeywordExtractor(
            lan="en",
            n=3,  # Extract up to 3-grams
            dedupLim=0.7,
            top=20,
        )

    def extract_keyphrases(self, text: str) -> List[str]:
        """
        Extract key phrases using YAKE algorithm.

        Args:
            text: Input text

        Returns:
            List of extracted keyphrases
        """
        try:
            keywords = self.yake_extractor.extract_keywords(text)
            # Return only the phrases, sorted by score (lower is better)
            return [phrase for score, phrase in keywords if score < 0.1]
        except Exception as e:
            logger.warning(f"YAKE extraction failed: {e}")
            # Fallback to simple word extraction
            return self._simple_phrase_extraction(text)

    def _simple_phrase_extraction(self, text: str) -> List[str]:
        """Fallback phrase extraction using regex."""
        # Extract noun phrases and compound words
        text = text.lower()
        phrases = re.findall(r'\b(?:\w+(?:\s+\w+){0,2})\b', text)
        return [p.strip() for p in phrases if len(p) > 3]

    def expand_synonyms(self, phrases: List[str]) -> Set[str]:
        """
        Expand phrases with synonyms and related terms.

        Args:
            phrases: List of keyphrases

        Returns:
            Set of expanded terms including synonyms
        """
        expanded = set(phrases)

        for phrase in phrases:
            phrase_lower = phrase.lower()

            # Check brand mappings
            for brand, alternatives in BRAND_MAPPINGS.items():
                if fuzz.partial_ratio(phrase_lower, brand) > 80:
                    expanded.update(alternatives)

            # Check synonym mappings
            for term, synonyms in SYNONYM_MAPPINGS.items():
                if fuzz.partial_ratio(phrase_lower, term) > 70:
                    expanded.update(synonyms)

            # Check location mappings
            for location, alternatives in LOCATION_MAPPINGS.items():
                if fuzz.partial_ratio(phrase_lower, location) > 80:
                    expanded.update(alternatives)

        return expanded

    def extract_brands(self, text: str) -> List[str]:
        """
        Extract brand names from text using fuzzy matching.

        Args:
            text: Input text

        Returns:
            List of detected brand names
        """
        text_lower = text.lower()
        detected_brands = []

        for brand in BRAND_MAPPINGS:
            if fuzz.partial_ratio(text_lower, brand) > 75:
                detected_brands.append(brand)

        return detected_brands

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for better processing.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Basic cleanup
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'[^\w\s\-\']', '', text)  # Keep only alphanumeric, spaces, hyphens, apostrophes
        text = text.strip().lower()

        return text

    def process_query(self, text: str) -> Dict[str, any]:
        """
        Process user query and extract all relevant information.

        Args:
            text: User input text

        Returns:
            Dictionary containing extracted information
        """
        normalized_text = self.normalize_text(text)
        keyphrases = self.extract_keyphrases(normalized_text)
        expanded_terms = self.expand_synonyms(keyphrases)
        brands = self.extract_brands(text)

        return {
            "original_text": text,
            "normalized_text": normalized_text,
            "keyphrases": keyphrases,
            "expanded_terms": list(expanded_terms),
            "brands": brands,
            "search_terms": list(expanded_terms.union(set(keyphrases))),
        }
