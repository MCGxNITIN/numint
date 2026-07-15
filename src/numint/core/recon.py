"""Recon link layer - an IntelTechniques-style "open all" phone tool.

Given a number, it fills a curated list of reverse-lookup and search-engine
URL templates (see `data/recon_sites.yaml`) so an investigator can open them
all at once for manual review. Like the footprint layer, it ONLY builds URLs.
It never scrapes, logs in, or automates against any site.

Most reverse-lookup sites are US/Canada (NANP) only, so those templates are
marked `scope: us` and skipped for other countries; search engines are global.
"""

from __future__ import annotations

import re
from functools import lru_cache
from importlib import resources
from urllib.parse import quote

import yaml

from .models import FootprintGroup, FootprintLink, ParsedNumber

_CATEGORY_TITLES = {
    "reverse_lookup": "Reverse Lookup / People Search",
    "search_engines": "Search Engines",
}


@lru_cache(maxsize=1)
def _load_sites() -> dict:
    with resources.files("numint.data").joinpath("recon_sites.yaml").open(
        "r", encoding="utf-8"
    ) as fh:
        return yaml.safe_load(fh) or {}


def _is_nanp(number: ParsedNumber, nsn: str) -> bool:
    """North American Numbering Plan (US/Canada/etc.): +1 with a 10-digit NSN."""
    return number.country_code == 1 and len(nsn) >= 10


def _substitutions(number: ParsedNumber) -> dict[str, str]:
    nsn = re.sub(r"\D", "", number.national)
    digits10 = nsn[:10] if len(nsn) >= 10 else nsn
    return {
        "area": nsn[0:3],
        "prefix": nsn[3:6],
        "suffix": nsn[6:10],
        "digits10": digits10,
        "natdigits": nsn,
        "digits": number.digits,
        "e164": number.e164,
        "plus_enc": quote(number.e164, safe=""),
        "iso": (number.country_iso or "us").lower(),
    }


def _fill(template: str, subs: dict[str, str]) -> str | None:
    try:
        return template.format(**subs)
    except (KeyError, IndexError):
        return None


def build_recon(number: ParsedNumber) -> list[FootprintGroup]:
    """Return grouped recon links for `number`, ready to open in a browser."""
    sites = _load_sites()
    subs = _substitutions(number)
    is_nanp = _is_nanp(number, subs["natdigits"])
    groups: list[FootprintGroup] = []

    for category, entries in sites.items():
        links: list[FootprintLink] = []
        for entry in entries or []:
            if entry.get("scope", "global") == "us" and not is_nanp:
                continue
            url = _fill(entry.get("template", ""), subs)
            if url:
                links.append(FootprintLink(label=entry["label"], url=url))
        if links:
            groups.append(
                FootprintGroup(
                    category=_CATEGORY_TITLES.get(category, category),
                    links=links,
                )
            )
    return groups


def recon_urls(number: ParsedNumber) -> list[str]:
    """Flat list of every recon URL (used by the CLI to open them)."""
    return [link.url for group in build_recon(number) for link in group.links]
