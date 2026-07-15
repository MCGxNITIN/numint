"""Tests for the lookup-site builder and dorking links (URL generation only)."""

from __future__ import annotations

from numint.core.footprint import build_dorking, dorking_urls
from numint.core.lookup import build_sites, site_urls
from numint.core.parser import parse_number


def test_top_only_is_a_small_curated_set():
    urls = site_urls(parse_number("+14155550123"))  # top_only=True default
    assert 0 < len(urls) <= 6  # "like 5 or less"
    assert any("thatsthem.com" in u for u in urls)


def test_all_sites_is_larger_than_top():
    number = parse_number("+14155550123")
    top = site_urls(number, top_only=True)
    everything = site_urls(number, top_only=False)
    assert len(everything) > len(top)


def test_us_number_splits_into_area_prefix_suffix():
    urls = site_urls(parse_number("+14155550123"), top_only=False)
    assert any("thatsthem.com/phone/415-555-0123" in u for u in urls)
    assert any("truepeoplesearch.com/results?phoneno=(415)555-0123" in u for u in urls)


def test_non_us_number_skips_us_only_sites():
    urls = site_urls(parse_number("+442079460958"), top_only=False)
    assert not any("thatsthem" in u for u in urls)
    assert not any("fastpeoplesearch" in u for u in urls)
    # Global sites (Sync.me / Truecaller) still present.
    assert any("sync.me" in u or "truecaller" in u for u in urls)


def test_no_sketchy_or_dead_sites():
    urls = site_urls(parse_number("+14155550123"), top_only=False)
    for bad in ("dehashed", "checkleaked", "americaphonebook", "oldphonebook"):
        assert not any(bad in u for u in urls), bad


def test_dorking_links_are_search_engines():
    urls = dorking_urls(parse_number("+14155550123"))
    assert urls
    assert any("google.com/search" in u for u in urls)
    assert all(u.startswith("http") for u in urls)


def test_dorking_group_titled():
    groups = build_dorking(parse_number("+14155550123"))
    assert groups and groups[0].category == "Search Engine Dorks"


def test_build_sites_returns_groups():
    groups = build_sites(parse_number("+14155550123"), top_only=False)
    assert groups and all(g.links for g in groups)
