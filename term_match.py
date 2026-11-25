"""Shared term matcher for SD5979 revision site.

CRITICAL: finalize_data.py (which rebuilds term occurrences) and build_site.py
(which wraps terms in HTML) MUST use this exact same matcher, otherwise the QA
coverage check would compare two different definitions of "occurrence".

It handles PPT line breaks and non-breaking spaces inside multi-word terms:
  "Laboratory\nexperiment"  -> "laboratory experiment"
  "Touch\xa0my\xa0heart"     -> "touch my heart"
"""
import re


def canon(s):
    """Normalise any whitespace (incl. NBSP) to single spaces, lowercase."""
    return re.sub(r"[\s\u00a0]+", " ", s.replace("\u00ad", "")).strip().lower()


def build_matcher(terms):
    """terms: dict key -> {'variants': [...]}. Returns (compiled PAT, lookup)."""
    lookup = {}
    for key, t in terms.items():
        for v in t["variants"]:
            lookup[canon(v)] = key
        lookup.setdefault(canon(key), key)
    # longest first so "independent samples t-test" wins over "t-test"
    variants = sorted(lookup, key=len, reverse=True)

    def pat(v):
        # each gap between words may be a space, a PPT line break, or an NBSP
        return r"[\s\u00a0]+".join(re.escape(w) for w in v.split())

    PAT = re.compile(
        r"(?<![A-Za-z0-9])(?:" + "|".join(pat(v) for v in variants) + r")(?![A-Za-z0-9])",
        re.I)
    return PAT, lookup
