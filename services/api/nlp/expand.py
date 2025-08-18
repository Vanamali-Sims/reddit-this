"""
Query expansion utilities for better search coverage.
"""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

# Domain-specific expansion rules
HAIR_SCALP_EXPANSIONS = {
    "flaky scalp": [
        "dandruff",
        "seborrheic dermatitis",
        "dry scalp",
        "scalp irritation",
        "white flakes",
        "itchy scalp",
    ],
    "hair loss": [
        "alopecia",
        "thinning hair",
        "balding",
        "hair fall",
        "receding hairline",
        "male pattern baldness",
        "female pattern hair loss",
    ],
    "oily hair": [
        "greasy hair",
        "sebaceous",
        "overproduction oil",
        "daily washing",
        "limp hair",
    ],
    "dry hair": [
        "dehydrated hair",
        "brittle hair",
        "lack moisture",
        "damaged cuticle",
        "protein loss",
    ],
    "itchy scalp": [
        "scalp irritation",
        "inflamed scalp",
        "sensitive scalp",
        "allergic reaction",
        "contact dermatitis",
    ],
    "damaged hair": [
        "breakage",
        "split ends",
        "chemical damage",
        "heat damage",
        "over processed",
        "protein loss",
        "moisture damage",
    ],
}

# Australian-specific expansions
AUSTRALIAN_EXPANSIONS = {
    "australia": [
        "aussie",
        "australian",
        "au",
        "down under",
        "chemist warehouse",
        "priceline",
        "terry white",
        "amcal",
    ],
    "pharmacies": [
        "chemist warehouse",
        "priceline pharmacy",
        "terry white chemmart",
        "amcal",
        "pharmacy",
        "chemist",
    ],
    "supermarkets": [
        "woolworths",
        "coles",
        "iga",
        "aldi australia",
    ],
}

# Treatment and ingredient expansions
TREATMENT_EXPANSIONS = {
    "antifungal": [
        "ketoconazole",
        "nizoral",
        "selenium sulfide",
        "selsun blue",
        "pyrithione zinc",
        "head shoulders",
    ],
    "gentle shampoo": [
        "sulfate free",
        "mild cleanser",
        "sensitive scalp",
        "baby shampoo",
        "low ph",
        "tear free",
    ],
    "moisturizing": [
        "hydrating",
        "nourishing",
        "conditioning",
        "repair",
        "ceramides",
        "hyaluronic acid",
        "natural oils",
    ],
    "natural remedies": [
        "tea tree oil",
        "apple cider vinegar",
        "coconut oil",
        "argan oil",
        "aloe vera",
        "honey",
    ],
}


class QueryExpander:
    """Expand user queries with related terms and concepts."""

    def __init__(self):
        self.expansions = {
            **HAIR_SCALP_EXPANSIONS,
            **AUSTRALIAN_EXPANSIONS,
            **TREATMENT_EXPANSIONS,
        }

    def expand_query_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """
        Expand query terms with related concepts.

        Args:
            terms: List of extracted terms from user query

        Returns:
            Dictionary mapping original terms to expanded terms
        """
        expansions = {}

        for term in terms:
            term_lower = term.lower()
            expanded = set()

            # Direct mapping check
            for key, values in self.expansions.items():
                if term_lower in key.lower() or any(
                    term_lower in v.lower() for v in values
                ):
                    expanded.update(values)

            # Fuzzy matching for partial matches
            expanded.update(self._fuzzy_expand(term_lower))

            if expanded:
                expansions[term] = list(expanded)

        return expansions

    def _fuzzy_expand(self, term: str) -> Set[str]:
        """
        Perform fuzzy expansion for partial term matches.

        Args:
            term: Term to expand

        Returns:
            Set of expanded terms
        """
        expanded = set()

        # Hair and scalp related expansions
        if any(word in term for word in ["flake", "flaky"]):
            expanded.update(HAIR_SCALP_EXPANSIONS.get("flaky scalp", []))

        if any(word in term for word in ["itch", "itchy"]):
            expanded.update(HAIR_SCALP_EXPANSIONS.get("itchy scalp", []))

        if any(word in term for word in ["oil", "oily", "grease", "greasy"]):
            expanded.update(HAIR_SCALP_EXPANSIONS.get("oily hair", []))

        if any(word in term for word in ["dry", "dehydrat"]):
            expanded.update(HAIR_SCALP_EXPANSIONS.get("dry hair", []))

        if any(word in term for word in ["loss", "thin", "bald"]):
            expanded.update(HAIR_SCALP_EXPANSIONS.get("hair loss", []))

        if any(word in term for word in ["damage", "break", "split"]):
            expanded.update(HAIR_SCALP_EXPANSIONS.get("damaged hair", []))

        # Australian context
        if any(word in term for word in ["aussie", "australia", "au"]):
            expanded.update(AUSTRALIAN_EXPANSIONS.get("australia", []))

        return expanded

    def create_search_variants(self, original_query: str, expanded_terms: Dict[str, List[str]]) -> List[str]:
        """
        Create multiple search query variants for better coverage.

        Args:
            original_query: Original user query
            expanded_terms: Dictionary of expanded terms

        Returns:
            List of query variants to search
        """
        variants = [original_query]

        # Create variants by substituting expanded terms
        for original_term, expansions in expanded_terms.items():
            for expansion in expansions[:3]:  # Limit to top 3 expansions
                variant = original_query.replace(original_term, expansion)
                if variant != original_query:
                    variants.append(variant)

        # Create combined expansion queries
        all_expansions = []
        for expansions in expanded_terms.values():
            all_expansions.extend(expansions[:2])  # Top 2 from each

        if all_expansions:
            # Create a query with top expanded terms
            expanded_query = " ".join(all_expansions[:5])
            variants.append(expanded_query)

        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant.lower() not in seen:
                seen.add(variant.lower())
                unique_variants.append(variant)

        return unique_variants[:10]  # Limit total variants
