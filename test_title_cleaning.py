#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced title cleaning functionality
"""

import re

def clean_title(filename):
    """Clean filename to extract just the movie/show title"""
    title = filename
    
    # Remove file extensions
    title = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm|m4v|3gp|ts|m2ts)$', '', title, flags=re.IGNORECASE)
    
    # Remove quality indicators
    quality_patterns = [
        r'\b(480p|720p|1080p|1440p|2160p|4k|8k)\b',
        r'\b(HD|FHD|UHD|QHD)\b',
        r'\b(CAM|TS|TC|SCR|DVDSCR|R5|DVDRip|BDRip|BRRip)\b',
        r'\b(WEBRip|WEB-DL|WEB|HDRip|BluRay|Bluray|BDRemux)\b',
        r'\b(HDCAM|HDTS|HDTC|PreDVDRip)\b'
    ]
    
    # Remove codec and format info
    codec_patterns = [
        r'\b(x264|x265|H264|H265|HEVC|AVC|XviD|DivX)\b',
        r'\b(AAC|AC3|DTS|MP3|FLAC|Atmos|TrueHD)\b',
        r'\b(10bit|8bit|HDR|SDR|Dolby|Vision)\b'
    ]
    
    # Remove source and release info
    source_patterns = [
        r'\b(AMZN|NF|HULU|DSNP|HBO|MAX|ATVP|PCOK|PMTP)\b',
        r'\b(Netflix|Amazon|Disney|Hotstar|Prime)\b',
        r'\b(REPACK|PROPER|REAL|RETAIL|EXTENDED|UNCUT|DC|IMAX)\b',
        r'\b(MULTI|DUAL|DUBBED|SUBBED|SUB|DUB)\b'
    ]
    
    # Remove language indicators
    language_patterns = [
        r'\b(Hindi|English|Tamil|Telugu|Malayalam|Kannada|Bengali|Punjabi|Gujarati|Marathi|Urdu)\b',
        r'\b(HINDI|ENGLISH|TAMIL|TELUGU|MALAYALAM|KANNADA|BENGALI|PUNJABI|GUJARATI|MARATHI|URDU)\b',
        r'\b(ORG|ORIGINAL|AUDIO)\b'
    ]
    
    # Remove years in parentheses and standalone
    title = re.sub(r'\(\d{4}\)', '', title)
    title = re.sub(r'\b(19|20)\d{2}\b', '', title)
    
    # Remove season/episode info
    title = re.sub(r'\b(S\d{1,2}|Season\s*\d{1,2})\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\b(E\d{1,2}|Episode\s*\d{1,2})\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\b(S\d{1,2}E\d{1,2})\b', '', title, flags=re.IGNORECASE)
    
    # Apply all cleaning patterns
    all_patterns = quality_patterns + codec_patterns + source_patterns + language_patterns
    for pattern in all_patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # Remove common separators and clean up
    title = re.sub(r'[\.\-_\[\]\(\)]+', ' ', title)
    title = re.sub(r'\s+', ' ', title)  # Multiple spaces to single space
    title = title.strip()
    
    # Remove common prefixes/suffixes
    title = re.sub(r'^(www\.|download|free|movie|film)\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*(download|free|movie|film)$', '', title, flags=re.IGNORECASE)
    
    return title

# Test cases based on your examples
test_files = [
    "Avengers: Endgame 1080P Bluray HEVC",
    "Avengers Endgame 720P WEB HEVC",
    "Avengers: Infinity 1080P WEB HEVC",
    "Avengers Triology 480P Bluray HEVC",
    "Avengers.Infinity.War.2018.1080p.BluRay.x264-SPARKS",
    "The.Matrix.1999.720p.BDRip.x264.AAC-YTS",
    "Spider-Man No Way Home (2021) 1080p WEBRip x265 HEVC 10bit AAC 5.1",
    "John.Wick.Chapter.4.2023.2160p.4K.WEB-DL.x265.10bit.HDR.DDP5.1.Atmos",
    "Game.of.Thrones.S08E06.The.Iron.Throne.1080p.AMZN.WEB-DL.DDP5.1.H.264"
]

print("Title Cleaning Test Results:")
print("=" * 60)
for filename in test_files:
    cleaned = clean_title(filename)
    print(f"Original: {filename}")
    print(f"Cleaned:  {cleaned}")
    print("-" * 60)
