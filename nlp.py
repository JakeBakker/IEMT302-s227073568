from __future__ import annotations

from typing import Dict, Optional
import re
from datetime import datetime

import spacy
from spacy.matcher import Matcher
import dateparser


class LostFoundNLP:
    """Lightweight NLP layer to parse lost/found/search intents and key fields."""

    COLOR_WORDS = {
        "black",
        "white",
        "red",
        "blue",
        "green",
        "yellow",
        "orange",
        "purple",
        "pink",
        "brown",
        "grey",
        "gray",
        "silver",
        "gold",
        "beige",
        "navy",
        "maroon",
        "teal",
        "turquoise",
    }

    def __init__(self) -> None:
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as exc:  # pragma: no cover - runtime environment
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' is not installed. Run: python -m spacy download en_core_web_sm"
            ) from exc
        self.matcher = Matcher(self.nlp.vocab)
        self._register_patterns()

    def _register_patterns(self) -> None:
        # lost intent patterns
        self.matcher.add(
            "INTENT_LOST",
            [
                [{"LOWER": {"IN": ["i", "i've", "ive"]}}, {"LOWER": {"IN": ["lost", "misplaced", "dropped", "left"]}}],
                [{"LOWER": {"IN": ["lost", "misplaced"]}}],
            ],
        )

        # found intent patterns
        self.matcher.add(
            "INTENT_FOUND",
            [
                [{"LOWER": "found"}],
                [{"LOWER": "i"}, {"LOWER": "found"}],
                [{"LOWER": "is"}, {"LOWER": "this"}, {"LOWER": {"IN": ["yours", "someone's", "someones"]}}],
            ],
        )

        # search intent patterns
        self.matcher.add(
            "INTENT_SEARCH",
            [
                [{"LOWER": {"IN": ["looking", "searching"]}}, {"LOWER": "for"}],
                [{"LOWER": "anyone"}, {"LOWER": "found"}],
            ],
        )

    def parse(self, text: str) -> Dict[str, Optional[str]]:
        doc = self.nlp(text)

        intent = self._infer_intent(doc)
        item = self._extract_item(doc)
        color = self._extract_color(doc)
        location = self._extract_location(doc)
        date_iso = self._extract_date_iso(doc)

        return {
            "intent": intent,
            "item": item,
            "color": color,
            "location": location,
            "date_iso": date_iso,
        }

    def _infer_intent(self, doc) -> Optional[str]:
        matches = self.matcher(doc)
        labels = {self.nlp.vocab[match_id].text for match_id, _, _ in matches}
        if "INTENT_LOST" in labels:
            return "lost"
        if "INTENT_FOUND" in labels:
            return "found"
        if "INTENT_SEARCH" in labels:
            return "search"

        lowered = doc.text.lower()
        if re.search(r"\b(lost|misplaced|left behind)\b", lowered):
            return "lost"
        if re.search(r"\b(found|picked up)\b", lowered):
            return "found"
        if re.search(r"\b(looking|searching) for\b", lowered):
            return "search"
        return None

    def _extract_item(self, doc) -> Optional[str]:
        candidate_nouns = [
            token.lemma_.lower()
            for token in doc
            if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop
        ]
        if not candidate_nouns:
            return None
        # Prefer the last noun chunk head as the item
        noun_chunks = list(doc.noun_chunks)
        if noun_chunks:
            head = noun_chunks[-1].root
            if head.lemma_.lower() in candidate_nouns:
                return head.text.lower()
        return candidate_nouns[-1]

    def _extract_color(self, doc) -> Optional[str]:
        adjectives = [t.text.lower() for t in doc if t.pos_ == "ADJ"]
        for adj in adjectives:
            if adj in self.COLOR_WORDS:
                return adj
        # Color words can also be nouns (e.g., silver)
        for token in doc:
            if token.text.lower() in self.COLOR_WORDS:
                return token.text.lower()
        return None

    def _extract_location(self, doc) -> Optional[str]:
        for ent in doc.ents:
            if ent.label_ in {"GPE", "LOC", "FAC"}:
                return ent.text
        preps = [t for t in doc if t.pos_ == "ADP" and t.lemma_ in {"at", "in", "near", "by", "around"}]
        if preps:
            prep = preps[-1]
            pobj = next((c for c in prep.children if c.dep_ == "pobj"), None)
            if pobj is not None:
                return pobj.text
        return None

    def _extract_date_iso(self, doc) -> Optional[str]:
        for ent in doc.ents:
            if ent.label_ == "DATE":
                parsed = dateparser.parse(ent.text)
                if parsed:
                    return parsed.date().isoformat()
        # Heuristic for words like yesterday/today
        lowered = doc.text.lower()
        if "yesterday" in lowered:
            return (datetime.utcnow().date()).isoformat()
        return None

