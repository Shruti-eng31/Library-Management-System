"""Program catalogue definitions used by BookFlow LMS."""

from __future__ import annotations

from itertools import chain
from typing import Dict, Iterable, List

PROGRAM_CATEGORIES: Dict[str, List[str]] = {
    "Artificial Intelligence": [
        "B.Tech (Artificial Intelligence)",
        "BCA (Artificial Intelligence)",
        "B.Sc. (Artificial Intelligence)",
    ],
    "Engineering": [
        "B.Tech (Computer Science Engineering)",
        "B.Tech (Electronics & Communication Engineering)",
        "B.Tech (Electronics & Computer Engineering)",
        "B.Tech (Mechanical Engineering)",
        "B.Tech (Engineering Physics)",
        "B.Tech (Biotech)",
        "B.Tech + M. Tech (Biotech) (Dual Degree)",
        "B.Tech + M.Tech (Computer Science & Engineering) (Dual Degree)",
        "BCA",
        "BCA + MCA (Dual Degree)",
    ],
    "Liberal Arts": [
        "B.A. (Hons.)",
        "B.A. (Hons.) Psychology",
        "B.A. (Hons.) Economics",
        "B.A. (Hons.) English Literature",
        "B.A. (Hons.) Sociology",
        "B.A. (Hons.) Philosophy",
        "B.A. (Hons.) Business Studies",
        "B.A. (Hons.) Political Science & International Relations",
    ],
    "Design": [
        "B. Des (Hons.)",
        "B. Des (Hons.) Fashion Design",
        "B. Des (Hons.) Intelligent Textile Design",
        "B. Des (Hons.) Product Design with AI",
        "B. Des (Hons.) Game Design",
        "B. Des (Hons.) Advanced Animation & VFX in partnership with CII",
        "B. Des (Hons.) Communication Design",
    ],
    "Management": [
        "BBA",
        "BBA + MBA (Dual Degree)",
        "B. Com (Finance & Accounting)",
        "B. Com (International Accounting & Finance) Integrated with ACCA",
    ],
    "Media": [
        "B.A. (Mass Communication)",
        "B.A. (Film, TV & Web Series)",
    ],
    "Law": [
        "Integ. BBA LL.B. (Hons.)",
        "Integ. B.A. LL.B. (Hons.)",
    ],
}


def all_programmes() -> List[str]:
    """Return a flattened list of every degree/programme we support."""
    return list(chain.from_iterable(PROGRAM_CATEGORIES.values()))


def programme_category(programme: str) -> str | None:
    """Look up the category for a programme name."""
    for category, programmes in PROGRAM_CATEGORIES.items():
        if programme in programmes:
            return category
    return None


def ensure_programme(programme: str) -> str:
    """Return programme if known, otherwise raise a ValueError."""
    if programme not in all_programmes():
        raise ValueError(f"Unknown programme: {programme}")
    return programme
