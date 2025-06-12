import logging
from struct import pack
import re
import base64
from hydrogram.file_id import FileId
from pymongo import MongoClient, TEXT
from pymongo.errors import DuplicateKeyError, OperationFailure
from info import USE_CAPTION_FILTER, FILES_DATABASE_URL, SECOND_FILES_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN

logger = logging.getLogger(__name__)

client = MongoClient(FILES_DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
try:
    collection.create_index([("file_name", TEXT)])
except OperationFailure as e:
    if 'quota' in str(e).lower():
        if not SECOND_FILES_DATABASE_URL:
            logger.error(f'your FILES_DATABASE_URL is already full, add SECOND_FILES_DATABASE_URL')
        else:
            logger.info('FILES_DATABASE_URL is full, now using SECOND_FILES_DATABASE_URL')
    else:
        logger.exception(e)

if SECOND_FILES_DATABASE_URL:
    second_client = MongoClient(SECOND_FILES_DATABASE_URL)
    second_db = second_client[DATABASE_NAME]
    second_collection = second_db[COLLECTION_NAME]
    second_collection.create_index([("file_name", TEXT)])


def second_db_count_documents():
     return second_collection.count_documents({})

def db_count_documents():
     return collection.count_documents({})


async def save_file(media):
    """Save file in database"""
    file_id = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    file_caption = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.caption))

    document = {
        '_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': file_caption
    }

    try:
        collection.insert_one(document)
        logger.info(f'Saved - {file_name}')
        return 'suc'
    except DuplicateKeyError:
        logger.warning(f'Already Saved - {file_name}')
        return 'dup'
    except OperationFailure:
        if SECOND_FILES_DATABASE_URL:
            try:
                second_collection.insert_one(document)
                logger.info(f'Saved to 2nd db - {file_name}')
                return 'suc'
            except DuplicateKeyError:
                logger.warning(f'Already Saved in 2nd db - {file_name}')
                return 'dup'
        else:
            logger.error(f'your FILES_DATABASE_URL is already full, add SECOND_FILES_DATABASE_URL')
            return 'err'

async def get_search_results(query, max_results=MAX_BTN, offset=0, lang=None):
    query = str(query).strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    cursor = collection.find(filter)
    results = [doc for doc in cursor]

    if SECOND_FILES_DATABASE_URL:
        cursor2 = second_collection.find(filter)
        results.extend([doc for doc in cursor2])

    if lang:
        lang_files = [file for file in results if lang in file['file_name'].lower()]
        files = lang_files[offset:][:max_results]
        total_results = len(lang_files)
        next_offset = offset + max_results
        if next_offset >= total_results:
            next_offset = ''
        return files, next_offset, total_results

    total_results = len(results)
    files = results[offset:][:max_results]
    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = ''
    return files, next_offset, total_results

async def delete_files(query):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query

    filter = {'file_name': regex}

    result1 = collection.delete_many(filter)

    result2 = None
    if SECOND_FILES_DATABASE_URL:
        result2 = second_collection.delete_many(filter)

    total_deleted = result1.deleted_count
    if result2:
        total_deleted += result2.deleted_count

    return total_deleted

async def get_file_details(query):
    file_details = collection.find_one({'_id': query})
    if not file_details and SECOND_FILES_DATABASE_URL:
        file_details = second_collection.find_one({'_id': query})
    return file_details

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id

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

async def get_distinct_titles(query):
    """Get distinct titles matching the search query"""
    query = str(query).strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query

    # Get distinct titles from both databases
    titles = set()

    # Search in primary database
    cursor = collection.find({'file_name': regex})
    for doc in cursor:
        # Clean the filename to extract just the title
        clean_title_text = clean_title(doc['file_name'])
        if clean_title_text and len(clean_title_text.strip()) > 2:  # Only add non-empty titles
            titles.add(clean_title_text)

    # Search in secondary database if available
    if SECOND_FILES_DATABASE_URL:
        cursor2 = second_collection.find({'file_name': regex})
        for doc in cursor2:
            clean_title_text = clean_title(doc['file_name'])
            if clean_title_text and len(clean_title_text.strip()) > 2:  # Only add non-empty titles
                titles.add(clean_title_text)

    # Filter out very short or meaningless titles
    filtered_titles = []
    for title in titles:
        if len(title.strip()) > 2 and not title.lower() in ['the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for']:
            filtered_titles.append(title.strip())

    return sorted(list(set(filtered_titles)))
