#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced title cleaning functionality
"""

import re

def clean_title(filename):
    """Clean filename to extract just the movie/show title"""
    title = filename

    # Remove file extensions first
    title = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm|m4v|3gp|ts|m2ts)$', '', title, flags=re.IGNORECASE)

    # Strategy: Extract title from beginning until we hit dates or season markers
    # Most titles are clean alphanumeric at the start, noise comes after

    # Find where the title likely ends by looking for:
    # 1. Year patterns (1900-2099)
    # 2. Season/Episode patterns (S01, S1, Season 1, etc.)
    # 3. Quality indicators that commonly appear after titles

    # Look for year patterns (movies): "Title.2023" or "Title (2023)" or "Title 2023"
    year_match = re.search(r'[\.\s\-_\(]+(19|20)\d{2}[\.\s\-_\)]', title)
    if year_match:
        title = title[:year_match.start()]

    # Look for season/episode patterns (series): "Title.S01E02" or "Title S1 E1"
    season_match = re.search(r'[\.\s\-_]+(S\d{1,2}|Season\s*\d{1,2})', title, flags=re.IGNORECASE)
    if season_match:
        title = title[:season_match.start()]

    # Look for common quality indicators that appear after titles
    quality_match = re.search(r'[\.\s\-_]+(480p|720p|1080p|2160p|4k|HD|FHD|UHD|BluRay|WEB|HDCAM|DVDRip|BDRip|WEBRip)', title, flags=re.IGNORECASE)
    if quality_match:
        title = title[:quality_match.start()]

    # Convert common separators to spaces
    title = re.sub(r'[\.\-_]+', ' ', title)

    # Clean up multiple spaces
    title = re.sub(r'\s+', ' ', title)

    # Remove leading/trailing whitespace
    title = title.strip()

    # Remove common prefixes that might appear at the start
    title = re.sub(r'^(www\.|download\s+|free\s+)', '', title, flags=re.IGNORECASE)

    # Handle special cases where title might have colons (like "Avengers: Endgame")
    # Keep colons as they're part of legitimate titles

    return title

# Test cases based on your examples and common patterns
test_files = [
    # Your original examples
    "Avengers: Endgame 1080P Bluray HEVC",
    "Avengers Endgame 720P WEB HEVC",
    "Avengers: Infinity 1080P WEB HEVC",
    "Avengers Triology 480P Bluray HEVC",

    # Movie examples with years
    "Sinners.2025.1080p.WEB-DL.x264",
    "The.Matrix.1999.720p.BDRip.x264.AAC",
    "Spider-Man.No.Way.Home.2021.1080p.WEBRip.x265.HEVC",
    "John.Wick.Chapter.4.2023.2160p.4K.WEB-DL.x265",
    "Avengers.Infinity.War.2018.1080p.BluRay.x264-SPARKS",

    # TV Series examples with seasons
    "The.Better.Sister.S01E02.1080p.WEB.x264",
    "Game.of.Thrones.S08E06.The.Iron.Throne.1080p.AMZN.WEB-DL",
    "Breaking.Bad.S05E14.Ozymandias.720p.BluRay.x264",
    "Stranger.Things.S04E01.The.Hellfire.Club.2160p.NF.WEB-DL",
    "The.Office.S02E01.The.Dundies.720p.WEB-DL",

    # Edge cases
    "The.Lord.of.the.Rings.The.Fellowship.of.the.Ring.2001.Extended.1080p",
    "Marvel's.Agents.of.S.H.I.E.L.D.S01E01.720p.HDTV",
    "Fast.and.Furious.9.The.Fast.Saga.2021.1080p.BluRay"
]

print("Title Cleaning Test Results:")
print("=" * 60)
for filename in test_files:
    cleaned = clean_title(filename)
    print(f"Original: {filename}")
    print(f"Cleaned:  {cleaned}")
    print("-" * 60)
