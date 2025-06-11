#!/usr/bin/env python3
"""
Video Cache Service - Quản lý cache video URLs trong Firestore
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from services.firestore_service import firestore_service

logger = logging.getLogger(__name__)

class VideoCacheService:
    """Service để cache video URLs trong Firestore"""
    
    def __init__(self):
        self.collection_name = 'dish_videos'
        self.cache_duration_days = 30  # Cache video URLs trong 30 ngày
        
    def _normalize_dish_name(self, dish_name: str) -> str:
        """
        Chuẩn hóa tên món ăn để làm key cache
        
        Args:
            dish_name: Tên món ăn gốc
            
        Returns:
            Tên món ăn đã được chuẩn hóa làm key
        """
        # Chuyển về lowercase và loại bỏ ký tự đặc biệt
        normalized = dish_name.lower().strip()
        
        # Loại bỏ các từ không cần thiết
        unnecessary_words = [
            'với', 'và', 'kèm', 'theo', 'kiểu', 'phong cách', 'đặc biệt',
            'truyền thống', 'gia đình', 'nhà làm', 'tự làm', 'món'
        ]
        
        for word in unnecessary_words:
            normalized = normalized.replace(f' {word} ', ' ')
            normalized = normalized.replace(f'{word} ', '')
            normalized = normalized.replace(f' {word}', '')
        
        # Loại bỏ khoảng trắng thừa và thay thế bằng underscore
        normalized = '_'.join(normalized.split())
        
        return normalized
    
    def get_cached_video(self, dish_name: str) -> Optional[str]:
        """
        Lấy video URL từ cache
        
        Args:
            dish_name: Tên món ăn
            
        Returns:
            Video URL nếu có trong cache, None nếu không có hoặc đã hết hạn
        """
        try:
            cache_key = self._normalize_dish_name(dish_name)
            
            # Lấy document từ Firestore
            doc_ref = firestore_service.db.collection(self.collection_name).document(cache_key)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.debug(f"Không tìm thấy cache cho món '{dish_name}' (key: {cache_key})")
                return None
            
            data = doc.to_dict()
            
            # Kiểm tra thời gian hết hạn
            cached_at = data.get('cached_at')
            if cached_at:
                # Chuyển đổi timestamp thành datetime
                if hasattr(cached_at, 'timestamp'):
                    cached_datetime = datetime.fromtimestamp(cached_at.timestamp())
                else:
                    cached_datetime = datetime.fromisoformat(str(cached_at))
                
                # Kiểm tra xem cache đã hết hạn chưa
                expiry_date = cached_datetime + timedelta(days=self.cache_duration_days)
                if datetime.now() > expiry_date:
                    logger.info(f"Cache cho món '{dish_name}' đã hết hạn, xóa cache")
                    doc_ref.delete()
                    return None
            
            video_url = data.get('video_url')
            if video_url:
                logger.info(f"✅ Tìm thấy cache video cho '{dish_name}': {video_url}")
                return video_url
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy cache video cho '{dish_name}': {str(e)}")
            return None
    
    def cache_video(self, dish_name: str, video_url: str, source: str = "youtube_api") -> bool:
        """
        Lưu video URL vào cache
        
        Args:
            dish_name: Tên món ăn
            video_url: URL của video
            source: Nguồn video (youtube_api, fallback, manual)
            
        Returns:
            True nếu lưu thành công, False nếu có lỗi
        """
        try:
            cache_key = self._normalize_dish_name(dish_name)
            
            cache_data = {
                'dish_name': dish_name,
                'normalized_name': cache_key,
                'video_url': video_url,
                'source': source,
                'cached_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Lưu vào Firestore
            doc_ref = firestore_service.db.collection(self.collection_name).document(cache_key)
            doc_ref.set(cache_data)
            
            logger.info(f"💾 Đã cache video cho '{dish_name}' (key: {cache_key}): {video_url}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi cache video cho '{dish_name}': {str(e)}")
            return False
    
    def update_video_cache(self, dish_name: str, video_url: str) -> bool:
        """
        Cập nhật video URL trong cache
        
        Args:
            dish_name: Tên món ăn
            video_url: URL video mới
            
        Returns:
            True nếu cập nhật thành công
        """
        try:
            cache_key = self._normalize_dish_name(dish_name)
            
            doc_ref = firestore_service.db.collection(self.collection_name).document(cache_key)
            doc_ref.update({
                'video_url': video_url,
                'updated_at': datetime.now()
            })
            
            logger.info(f"🔄 Đã cập nhật cache video cho '{dish_name}': {video_url}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật cache video cho '{dish_name}': {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê cache
        
        Returns:
            Dictionary chứa thống kê cache
        """
        try:
            collection_ref = firestore_service.db.collection(self.collection_name)
            docs = collection_ref.get()
            
            total_cached = len(docs)
            sources = {}
            
            for doc in docs:
                data = doc.to_dict()
                source = data.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
            
            return {
                'total_cached_videos': total_cached,
                'sources': sources,
                'cache_duration_days': self.cache_duration_days
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê cache: {str(e)}")
            return {'error': str(e)}

# Tạo instance global
video_cache_service = VideoCacheService()
