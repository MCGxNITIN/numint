"""Tests for the recon link builder (URL generation only)."""

from __future__ import annotations

from numint.core.parser import parse_number
from numint.core.recon import build_recon, recon_urls


def test_us_number_gets_reverse_lookup_and_search():
    number = parse_number("+14155550123")
    cats = {g.category for g in build_recon(number)}
    assert "Reverse Lookup / People Search" in cats
    assert "Search Engines" in cats


def test_us_number_splits_into_area_prefix_suffix():
    urls = recon_urls(parse_number("+14155550123"))
    assert any("thatsthem.com/phone/415-555-0123" in u for u in urls)
    assert any("truepeoplesearch.com/results?phoneno=(415)555-0123" in u for u in urls)


def test_non_us_number_skips_us_only_sites():
    urls = recon_urls(parse_number("+442079460958"))
    # US people-search sites are scope: us and must be skipped.
    assert not any("thatsthem" in u for u in urls)
    assert not any("fastpeoplesearch" in u for u in urls)
    # Global search engines still present.
    assert any("google.com/search" in u for u in urls)


def test_sketchy_and_dead_sites_are_not_included():
    urls = recon_urls(parse_number("+14155550123"))
    for bad in ("dehashed", "checkleaked", "americaphonebook", "oldphonebook"):
        assert not any(bad in u for u in urls), bad


def test_recon_urls_flat_and_nonempty():
    urls = recon_urls(parse_number("+14155550123"))
    assert len(urls) > 20
    assert all(u.startswith("http") for u in urls)
