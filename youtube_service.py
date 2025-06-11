"""
YouTube Video Search Service
Tự động tìm kiếm video hướng dẫn nấu ăn trên YouTube cho các món ăn
"""

import requests
import os
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote_plus
import time
from services.video_cache_service import video_cache_service

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service để tự động tìm kiếm video YouTube cho món ăn"""
    
    def __init__(self):
        self.api_key = os.environ.get("YOUTUBE_API_KEY")
        self.base_url = "https://www.googleapis.com/youtube/v3/search"
        self.available = bool(self.api_key)

        # Fallback video URLs cho các món ăn phổ biến (URLs thật về nấu ăn)
        self.fallback_videos = {
            # Món chính
            'phở': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'cơm': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'bánh mì': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'bún': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'canh': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'xôi': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'chả': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'mì': 'https://www.youtube.com/watch?v=np1HMXdPqcM',

            # Protein
            'gà': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'thịt': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'cá': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'tôm': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'sườn': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'trứng': 'https://www.youtube.com/watch?v=np1HMXdPqcM',

            # Rau củ và chay
            'rau': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'đậu': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'chay': 'https://www.youtube.com/watch?v=np1HMXdPqcM',

            # Bánh kẹo và món tráng miệng
            'bánh': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'waffle': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'pancake': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'sandwich': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'salad': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'smoothie': 'https://www.youtube.com/watch?v=np1HMXdPqcM',

            # Từ khóa chung
            'nướng': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'xào': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'luộc': 'https://www.youtube.com/watch?v=np1HMXdPqcM',
            'chiên': 'https://www.youtube.com/watch?v=np1HMXdPqcM'
        }

        if not self.available:
            logger.warning("YouTube API Key không được cấu hình. Sử dụng fallback video URLs.")
        else:
            logger.info("YouTube Service đã được khởi tạo thành công.")
    
    def _normalize_dish_name(self, dish_name: str) -> str:
        """
        Chuẩn hóa tên món ăn để tìm kiếm tốt hơn

        Args:
            dish_name: Tên món ăn gốc

        Returns:
            Tên món ăn đã được chuẩn hóa
        """
        # Loại bỏ các từ không cần thiết
        unnecessary_words = [
            'với', 'và', 'kèm', 'theo', 'kiểu', 'phong cách', 'đặc biệt',
            'truyền thống', 'gia đình', 'nhà làm', 'tự làm'
        ]

        normalized = dish_name.lower()
        for word in unnecessary_words:
            normalized = normalized.replace(word, ' ')

        # Loại bỏ khoảng trắng thừa
        normalized = ' '.join(normalized.split())

        return normalized

    def _get_fallback_video(self, dish_name: str) -> Optional[str]:
        """
        Tìm fallback video URL dựa trên tên món ăn

        Args:
            dish_name: Tên món ăn

        Returns:
            URL fallback video hoặc None
        """
        dish_lower = dish_name.lower()

        # Tìm kiếm từ khóa trong tên món ăn
        for keyword, video_url in self.fallback_videos.items():
            if keyword in dish_lower:
                logger.info(f"🎯 Tìm thấy fallback video cho '{dish_name}' với keyword '{keyword}'")
                return video_url

        # Nếu không tìm thấy keyword cụ thể, trả về video mặc định
        default_video = 'https://www.youtube.com/watch?v=np1HMXdPqcM'
        logger.info(f"📺 Sử dụng default video cho '{dish_name}'")
        return default_video

    def get_youtube_video_url(self, dish_name: str, max_retries: int = 3) -> Optional[str]:
        """
        Tìm kiếm video YouTube cho món ăn với cache optimization

        Args:
            dish_name: Tên món ăn cần tìm video
            max_retries: Số lần thử lại tối đa

        Returns:
            URL của video YouTube hoặc None nếu không tìm thấy
        """
        logger.info(f"🔍 Tìm kiếm video cho món '{dish_name}'")

        # BƯỚC 1: Kiểm tra cache trước
        cached_video = video_cache_service.get_cached_video(dish_name)
        if cached_video:
            logger.info(f"✅ Sử dụng cached video cho '{dish_name}': {cached_video}")
            return cached_video

        # BƯỚC 2: Thử tìm fallback video
        fallback_url = self._get_fallback_video(dish_name)
        if fallback_url:
            logger.info(f"📋 Sử dụng fallback video cho '{dish_name}': {fallback_url}")
            # Cache fallback video để lần sau không phải tìm lại
            video_cache_service.cache_video(dish_name, fallback_url, "fallback")
            return fallback_url

        # BƯỚC 3: Nếu không có cache và fallback, thử YouTube API
        if not self.available:
            logger.warning("YouTube API không khả dụng và không có fallback video")
            return None

        # Chuẩn hóa tên món ăn cho tìm kiếm
        normalized_name = self._normalize_dish_name(dish_name)
        logger.info(f"🔍 Tìm kiếm trên YouTube API cho '{dish_name}' (chuẩn hóa: '{normalized_name}')")

        # Tạo query tìm kiếm với nhiều biến thể hơn
        search_queries = [
            f"cách làm {normalized_name}",
            f"hướng dẫn nấu {normalized_name}",
            f"công thức {normalized_name}",
            f"nấu {normalized_name}",
            f"làm {normalized_name}",
            f"recipe {normalized_name}",
            f"{normalized_name} recipe",
            f"{normalized_name} cooking tutorial",
            f"how to make {normalized_name}",
            f"{normalized_name} cooking",
            # Thêm query với tên gốc nếu khác với tên chuẩn hóa
            f"cách làm {dish_name}" if normalized_name != dish_name.lower() else None,
            f"recipe {dish_name}" if normalized_name != dish_name.lower() else None
        ]

        # Loại bỏ các query None
        search_queries = [q for q in search_queries if q is not None]
        
        for query in search_queries:
            try:
                video_url = self._search_video(query)
                if video_url:
                    logger.info(f"✅ Tìm thấy video cho '{dish_name}': {video_url}")

                    # BƯỚC 4: Cache kết quả tìm kiếm
                    video_cache_service.cache_video(dish_name, video_url, "youtube_api")
                    return video_url
                    
                # Delay giữa các query để tránh rate limit
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Lỗi khi tìm kiếm video với query '{query}': {str(e)}")
                continue
        
        logger.warning(f"Không tìm thấy video phù hợp cho món '{dish_name}'")
        return None
    
    def _search_video(self, query: str) -> Optional[str]:
        """
        Thực hiện tìm kiếm video với query cụ thể
        
        Args:
            query: Từ khóa tìm kiếm
            
        Returns:
            URL của video hoặc None
        """
        try:
            # Encode query để đảm bảo URL hợp lệ
            encoded_query = quote_plus(query)
            
            # Tham số cho API request
            params = {
                'part': 'snippet',
                'q': encoded_query,
                'key': self.api_key,
                'maxResults': 5,  # Lấy 5 kết quả để có nhiều lựa chọn
                'type': 'video',
                'order': 'relevance',  # Sắp xếp theo độ liên quan
                'regionCode': 'VN',  # Ưu tiên kết quả từ Việt Nam
                'relevanceLanguage': 'vi'  # Ưu tiên ngôn ngữ tiếng Việt
            }
            
            # Gửi request đến YouTube API
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Kiểm tra có kết quả không
            if 'items' not in data or not data['items']:
                return None
            
            # Tìm video phù hợp nhất
            for item in data['items']:
                video_id = item['id']['videoId']
                title = item['snippet']['title'].lower()
                description = item['snippet']['description'].lower()
                
                # Kiểm tra video có liên quan đến nấu ăn không
                cooking_keywords = [
                    'cách làm', 'hướng dẫn', 'công thức', 'nấu', 'làm', 'chế biến',
                    'recipe', 'cooking', 'tutorial', 'how to make', 'food', 'kitchen',
                    'chef', 'món', 'ăn', 'thức ăn', 'bếp'
                ]

                # Nếu tìm thấy từ khóa nấu ăn, ưu tiên video này
                if any(keyword in title or keyword in description for keyword in cooking_keywords):
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    logger.info(f"✅ Tìm thấy cooking video: {title}")
                    return video_url

            # Nếu không có video nào phù hợp, trả về video đầu tiên
            if data['items']:
                video_id = data['items'][0]['id']['videoId']
                title = data['items'][0]['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                logger.info(f"📺 Sử dụng video đầu tiên: {title}")
                return video_url

            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi network khi gọi YouTube API: {str(e)}")
            return None
        except KeyError as e:
            logger.error(f"Lỗi parse response từ YouTube API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi tìm kiếm video: {str(e)}")
            return None
    
    def get_video_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết của video từ URL
        
        Args:
            video_url: URL của video YouTube
            
        Returns:
            Dictionary chứa thông tin video hoặc None
        """
        if not self.available:
            return None
            
        try:
            # Extract video ID từ URL
            if 'watch?v=' in video_url:
                video_id = video_url.split('watch?v=')[1].split('&')[0]
            else:
                return None
            
            # Gọi API để lấy thông tin video
            params = {
                'part': 'snippet,statistics',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' not in data or not data['items']:
                return None
            
            item = data['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            
            return {
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_title': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'view_count': statistics.get('viewCount', '0'),
                'like_count': statistics.get('likeCount', '0'),
                'duration': item.get('contentDetails', {}).get('duration', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin video: {str(e)}")
            return None

# Tạo instance global
youtube_service = YouTubeService()
