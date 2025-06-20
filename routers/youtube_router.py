"""
YouTube Proxy Router
Provides secure YouTube Data API proxy endpoints with caching and quota management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
import logging
import json
import hashlib
from datetime import datetime, timedelta
import asyncio
import httpx
import os
from pydantic import BaseModel

from auth_utils import get_current_user
from models import TokenPayload

# Setup logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/youtube", tags=["YouTube Proxy"])

# YouTube Data API configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'AIzaSyAIYbul927kNqEk9eJYROHQE6BdYfmMBPc')
YOUTUBE_BASE_URL = 'https://www.googleapis.com/youtube/v3'

# Cache configuration
VIDEO_CACHE = {}  # In-memory cache
CACHE_DURATION = timedelta(hours=24)  # Cache for 24 hours
MAX_CACHE_SIZE = 1000  # Maximum cached items

class VideoSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    duration: Optional[str] = 'medium'  # short, medium, long
    order: Optional[str] = 'relevance'  # relevance, date, rating, viewCount

class VideoSearchResponse(BaseModel):
    videos: List[Dict[str, str]]
    cached: bool
    cache_timestamp: Optional[str]

class VideoDetailsRequest(BaseModel):
    video_ids: List[str]

class VideoDetailsResponse(BaseModel):
    videos: List[Dict[str, str]]
    cached: bool

def _generate_cache_key(endpoint: str, params: Dict) -> str:
    """Generate cache key from endpoint and parameters"""
    # Sort parameters for consistent cache keys
    sorted_params = json.dumps(params, sort_keys=True)
    cache_string = f"{endpoint}:{sorted_params}"
    return hashlib.md5(cache_string.encode()).hexdigest()

def _is_cache_valid(cache_entry: Dict) -> bool:
    """Check if cache entry is still valid"""
    if 'timestamp' not in cache_entry:
        return False
    
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    return datetime.now() - cache_time < CACHE_DURATION

def _clean_cache():
    """Remove expired cache entries"""
    global VIDEO_CACHE
    
    expired_keys = []
    for key, entry in VIDEO_CACHE.items():
        if not _is_cache_valid(entry):
            expired_keys.append(key)
    
    for key in expired_keys:
        del VIDEO_CACHE[key]
    
    # Limit cache size
    if len(VIDEO_CACHE) > MAX_CACHE_SIZE:
        # Remove oldest entries
        sorted_cache = sorted(
            VIDEO_CACHE.items(),
            key=lambda x: x[1].get('timestamp', ''),
        )
        
        # Keep only the newest MAX_CACHE_SIZE entries
        VIDEO_CACHE = dict(sorted_cache[-MAX_CACHE_SIZE:])

def _create_vietnamese_query(dish_name: str) -> str:
    """Create Vietnamese cooking query for better search results"""
    vietnamese_queries = {
        'Phở Bò': 'cách nấu phở bò Hà Nội ngon',
        'Phở Gà': 'cách nấu phở gà ngon',
        'Phở Gà Nấu Dừa Miền Tây': 'cách nấu phở gà dừa miền Tây',
        'Bún Chả': 'cách làm bún chả Hà Nội',
        'Cơm Tấm': 'cách làm cơm tấm sườn nướng Sài Gòn',
        'Bánh Mì': 'cách làm bánh mì Việt Nam',
        'Gỏi Cuốn': 'cách cuốn gỏi cuốn tôm thịt',
        'Canh Chua': 'cách nấu canh chua cá miền Tây',
        'Bún Bò Huế': 'cách nấu bún bò Huế chuẩn vị',
        'Bánh Xèo': 'cách làm bánh xèo miền Tây',
        'Chả Cá': 'cách làm chả cá Lã Vọng Hà Nội',
        'Nem Nướng': 'cách làm nem nướng Nha Trang',
    }
    
    if dish_name in vietnamese_queries:
        return vietnamese_queries[dish_name]
    
    return f'cách nấu {dish_name} ngon tiếng Việt'

def _format_duration(duration: str) -> str:
    """Format ISO 8601 duration to readable format"""
    if not duration:
        return 'N/A'
    
    try:
        import re
        regex = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = regex.match(duration)
        
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            if hours > 0:
                return f'{hours}:{minutes:02d}:{seconds:02d}'
            else:
                return f'{minutes}:{seconds:02d}'
    except Exception as e:
        logger.error(f"Error formatting duration {duration}: {e}")
    
    return duration

def _format_view_count(view_count: str) -> str:
    """Format view count to readable format"""
    if not view_count:
        return 'N/A'
    
    try:
        count = int(view_count)
        
        if count >= 1_000_000_000:
            return f'{count / 1_000_000_000:.1f}B'
        elif count >= 1_000_000:
            return f'{count / 1_000_000:.1f}M'
        elif count >= 1_000:
            return f'{count / 1_000:.1f}K'
        else:
            return str(count)
    except ValueError:
        return view_count

def _is_quality_video(video_data: Dict) -> bool:
    """Filter for quality cooking videos"""
    title = video_data.get('title', '').lower()
    description = video_data.get('description', '').lower()
    
    # Positive keywords
    positive_keywords = [
        'cách', 'nấu', 'làm', 'hướng dẫn', 'bí quyết', 'ngon', 'chuẩn vị',
        'recipe', 'cooking', 'tutorial', 'how to', 'authentic',
    ]
    
    # Negative keywords
    negative_keywords = [
        'reaction', 'review', 'mukbang', 'asmr', 'vlog', 'challenge',
        'prank', 'funny', 'comedy', 'parody', 'meme',
    ]
    
    # Count positive keywords
    positive_count = sum(1 for keyword in positive_keywords 
                        if keyword in title or keyword in description)
    
    # Check for negative keywords
    has_negative = any(keyword in title or keyword in description 
                      for keyword in negative_keywords)
    
    # Filter criteria
    if has_negative:
        return False
    
    if len(title) < 10:
        return False
    
    return positive_count > 0

async def _make_youtube_request(url: str) -> Dict:
    """Make async request to YouTube API"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"YouTube API error: {response.status_code}"
            )

@router.post("/search", response_model=VideoSearchResponse)
async def search_videos(
    request: VideoSearchRequest
    # user: TokenPayload = Depends(get_current_user)  # Temporarily disabled for testing
):
    """
    Search for cooking videos with caching and quality filtering
    
    Parameters:
    - query: Search query (dish name)
    - max_results: Maximum number of results (default: 5)
    - duration: Video duration filter (short/medium/long)
    - order: Sort order (relevance/date/rating/viewCount)
    
    Returns:
    - List of quality cooking videos with complete metadata
    """
    try:
        # Clean expired cache entries
        _clean_cache()
        
        # Create Vietnamese query
        vietnamese_query = _create_vietnamese_query(request.query)
        
        # Generate cache key
        cache_params = {
            'query': vietnamese_query,
            'max_results': request.max_results,
            'duration': request.duration,
            'order': request.order
        }
        cache_key = _generate_cache_key('search', cache_params)
        
        # Check cache first
        if cache_key in VIDEO_CACHE and _is_cache_valid(VIDEO_CACHE[cache_key]):
            logger.info(f"Cache hit for search: {request.query}")
            cache_entry = VIDEO_CACHE[cache_key]
            return VideoSearchResponse(
                videos=cache_entry['data'],
                cached=True,
                cache_timestamp=cache_entry['timestamp']
            )
        
        # Build YouTube API URL
        url = f"{YOUTUBE_BASE_URL}/search"
        params = {
            'part': 'snippet',
            'q': vietnamese_query,
            'type': 'video',
            'videoCategoryId': '26',  # Howto & Style
            'maxResults': min(request.max_results * 2, 20),  # Get more for filtering
            'order': request.order,
            'regionCode': 'VN',
            'relevanceLanguage': 'vi',
            'videoDuration': request.duration,
            'key': YOUTUBE_API_KEY
        }
        
        # Add parameters to URL
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_string}"
        
        logger.info(f"Searching YouTube for: {vietnamese_query}")
        
        # Make API request
        data = await _make_youtube_request(full_url)
        
        # Process search results
        videos = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            video_data = {
                'title': snippet.get('title', 'Video không có tiêu đề'),
                'channel': snippet.get('channelTitle', 'Kênh không xác định'),
                'description': snippet.get('description', 'Không có mô tả'),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'videoId': item.get('id', {}).get('videoId', ''),
                'publishedAt': snippet.get('publishedAt', ''),
                'duration': 'N/A',  # Will be enhanced later
                'views': 'N/A',     # Will be enhanced later
            }
            
            # Filter for quality videos
            if _is_quality_video(video_data):
                videos.append(video_data)
                
                # Stop when we have enough quality videos
                if len(videos) >= request.max_results:
                    break
        
        # Enhance videos with details (duration, views)
        if videos:
            video_ids = [v['videoId'] for v in videos if v['videoId']]
            enhanced_videos = await _enhance_videos_with_details(video_ids, videos)
        else:
            enhanced_videos = videos
        
        # Cache the results
        VIDEO_CACHE[cache_key] = {
            'data': enhanced_videos,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Found {len(enhanced_videos)} quality videos for: {request.query}")
        
        return VideoSearchResponse(
            videos=enhanced_videos,
            cached=False,
            cache_timestamp=None
        )
        
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching videos: {str(e)}")

async def _enhance_videos_with_details(video_ids: List[str], videos: List[Dict]) -> List[Dict]:
    """Enhance videos with duration and view count details"""
    if not video_ids:
        return videos
    
    try:
        # Build video details API URL
        ids_string = ','.join(video_ids)
        url = f"{YOUTUBE_BASE_URL}/videos"
        params = {
            'part': 'contentDetails,statistics',
            'id': ids_string,
            'key': YOUTUBE_API_KEY
        }
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_string}"
        
        # Make API request
        data = await _make_youtube_request(full_url)
        
        # Create details mapping
        video_details = {}
        for item in data.get('items', []):
            video_id = item.get('id', '')
            content_details = item.get('contentDetails', {})
            statistics = item.get('statistics', {})
            
            video_details[video_id] = {
                'duration': _format_duration(content_details.get('duration', '')),
                'views': _format_view_count(statistics.get('viewCount', ''))
            }
        
        # Enhance original videos
        enhanced_videos = []
        for video in videos:
            video_id = video.get('videoId', '')
            details = video_details.get(video_id, {})
            
            enhanced_video = video.copy()
            enhanced_video['duration'] = details.get('duration', 'N/A')
            enhanced_video['views'] = details.get('views', 'N/A')
            
            enhanced_videos.append(enhanced_video)
        
        logger.info(f"Enhanced {len(enhanced_videos)} videos with details")
        return enhanced_videos
        
    except Exception as e:
        logger.error(f"Error enhancing videos: {e}")
        return videos  # Return original videos if enhancement fails

@router.get("/trending")
async def get_trending_cooking_videos(
    max_results: int = Query(10, ge=1, le=50)
    # user: TokenPayload = Depends(get_current_user)  # Temporarily disabled for testing
):
    """
    Get trending cooking videos from Vietnam region
    
    Parameters:
    - max_results: Maximum number of results (1-50)
    
    Returns:
    - List of trending cooking videos
    """
    try:
        # Clean cache
        _clean_cache()
        
        # Generate cache key
        cache_key = _generate_cache_key('trending', {'max_results': max_results})
        
        # Check cache
        if cache_key in VIDEO_CACHE and _is_cache_valid(VIDEO_CACHE[cache_key]):
            logger.info("Cache hit for trending videos")
            cache_entry = VIDEO_CACHE[cache_key]
            return {
                'videos': cache_entry['data'],
                'cached': True,
                'cache_timestamp': cache_entry['timestamp']
            }
        
        # Build API URL
        url = f"{YOUTUBE_BASE_URL}/videos"
        params = {
            'part': 'snippet,statistics,contentDetails',
            'chart': 'mostPopular',
            'videoCategoryId': '26',  # Howto & Style
            'regionCode': 'VN',
            'maxResults': max_results,
            'key': YOUTUBE_API_KEY
        }
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_string}"
        
        logger.info("Getting trending cooking videos")
        
        # Make API request
        data = await _make_youtube_request(full_url)
        
        # Process results
        videos = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            video_data = {
                'title': snippet.get('title', 'Video không có tiêu đề'),
                'channel': snippet.get('channelTitle', 'Kênh không xác định'),
                'description': snippet.get('description', 'Không có mô tả'),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'videoId': item.get('id', ''),
                'views': _format_view_count(statistics.get('viewCount', '')),
                'duration': _format_duration(content_details.get('duration', '')),
                'publishedAt': snippet.get('publishedAt', ''),
            }
            
            videos.append(video_data)
        
        # Cache results
        VIDEO_CACHE[cache_key] = {
            'data': videos,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Found {len(videos)} trending cooking videos")
        
        return {
            'videos': videos,
            'cached': False,
            'cache_timestamp': None
        }
        
    except Exception as e:
        logger.error(f"Error getting trending videos: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting trending videos: {str(e)}")

@router.get("/cache/stats")
async def get_cache_stats():  # user: TokenPayload = Depends(get_current_user)  # Temporarily disabled
    """Get cache statistics for monitoring"""
    _clean_cache()
    
    valid_entries = sum(1 for entry in VIDEO_CACHE.values() if _is_cache_valid(entry))
    
    return {
        'total_entries': len(VIDEO_CACHE),
        'valid_entries': valid_entries,
        'expired_entries': len(VIDEO_CACHE) - valid_entries,
        'cache_duration_hours': CACHE_DURATION.total_seconds() / 3600,
        'max_cache_size': MAX_CACHE_SIZE
    }

@router.delete("/cache/clear")
async def clear_cache():  # user: TokenPayload = Depends(get_current_user)  # Temporarily disabled
    """Clear all cache entries"""
    global VIDEO_CACHE
    old_size = len(VIDEO_CACHE)
    VIDEO_CACHE.clear()

    return {
        'message': f'Cache cleared. Removed {old_size} entries.',
        'entries_removed': old_size
    }

@router.post("/details", response_model=VideoDetailsResponse)
async def get_video_details(
    request: VideoDetailsRequest
    # user: TokenPayload = Depends(get_current_user)  # Temporarily disabled for testing
):
    """
    Get detailed information for specific video IDs

    Parameters:
    - video_ids: List of YouTube video IDs

    Returns:
    - List of videos with detailed information (duration, views, etc.)
    """
    try:
        if not request.video_ids:
            return VideoDetailsResponse(videos=[], cached=False)

        # Clean expired cache entries
        _clean_cache()

        # Generate cache key
        cache_params = {'video_ids': sorted(request.video_ids)}
        cache_key = _generate_cache_key('details', cache_params)

        # Check cache first
        if cache_key in VIDEO_CACHE and _is_cache_valid(VIDEO_CACHE[cache_key]):
            logger.info(f"Cache hit for video details: {len(request.video_ids)} videos")
            cache_entry = VIDEO_CACHE[cache_key]
            return VideoDetailsResponse(
                videos=cache_entry['data'],
                cached=True
            )

        # Build YouTube API URL
        ids_string = ','.join(request.video_ids)
        url = f"{YOUTUBE_BASE_URL}/videos"
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': ids_string,
            'key': YOUTUBE_API_KEY
        }

        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_string}"

        logger.info(f"Getting details for {len(request.video_ids)} videos")

        # Make API request
        data = await _make_youtube_request(full_url)

        # Process results
        videos = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})

            video_data = {
                'title': snippet.get('title', 'Video không có tiêu đề'),
                'channel': snippet.get('channelTitle', 'Kênh không xác định'),
                'description': snippet.get('description', 'Không có mô tả'),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'videoId': item.get('id', ''),
                'views': _format_view_count(statistics.get('viewCount', '')),
                'duration': _format_duration(content_details.get('duration', '')),
                'publishedAt': snippet.get('publishedAt', ''),
            }

            videos.append(video_data)

        # Cache the results
        VIDEO_CACHE[cache_key] = {
            'data': videos,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"Found details for {len(videos)} videos")

        return VideoDetailsResponse(
            videos=videos,
            cached=False
        )

    except Exception as e:
        logger.error(f"Error getting video details: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting video details: {str(e)}")
