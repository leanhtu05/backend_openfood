"""
Dish Enhancement Service
Tự động cải thiện thông tin món ăn bằng cách thêm video URL và các thông tin khác
"""

import logging
from typing import List, Optional
from models import Dish
from youtube_service import youtube_service
import asyncio
import concurrent.futures
from functools import partial

logger = logging.getLogger(__name__)

class DishEnhancementService:
    """Service để tự động cải thiện thông tin món ăn"""
    
    def __init__(self):
        self.youtube_service = youtube_service
        self.max_workers = 3  # Số thread tối đa để tìm kiếm video song song
    
    def enhance_dish_with_video(self, dish: Dish) -> Dish:
        """
        Thêm video URL cho một món ăn
        
        Args:
            dish: Đối tượng Dish cần cải thiện
            
        Returns:
            Dish đã được cải thiện với video URL
        """
        try:
            # Nếu đã có video URL thì không cần tìm nữa
            if dish.video_url:
                logger.info(f"Món '{dish.name}' đã có video URL: {dish.video_url}")
                return dish
            
            # Tìm kiếm video cho món ăn
            logger.info(f"Đang tìm kiếm video cho món '{dish.name}'...")
            video_url = self.youtube_service.get_youtube_video_url(dish.name)
            
            if video_url:
                # Tạo bản sao của dish với video URL mới
                enhanced_dish = Dish(
                    name=dish.name,
                    ingredients=dish.ingredients,
                    preparation=dish.preparation,
                    nutrition=dish.nutrition,
                    dish_type=dish.dish_type,
                    region=dish.region,
                    image_url=dish.image_url,
                    video_url=video_url,  # Thêm video URL
                    preparation_time=dish.preparation_time,
                    health_benefits=dish.health_benefits
                )
                
                logger.info(f"Đã thêm video cho món '{dish.name}': {video_url}")
                return enhanced_dish
            else:
                logger.warning(f"Không tìm thấy video phù hợp cho món '{dish.name}'")
                return dish
                
        except Exception as e:
            logger.error(f"Lỗi khi tìm video cho món '{dish.name}': {str(e)}")
            return dish
    
    def enhance_dishes_with_videos(self, dishes: List[Dish]) -> List[Dish]:
        """
        Thêm video URL cho danh sách món ăn (xử lý song song)
        
        Args:
            dishes: Danh sách các món ăn cần cải thiện
            
        Returns:
            Danh sách món ăn đã được cải thiện
        """
        if not dishes:
            return dishes
        
        logger.info(f"Đang cải thiện {len(dishes)} món ăn với video URLs...")
        
        # Nếu YouTube service không khả dụng, trả về danh sách gốc
        if not self.youtube_service.available:
            logger.warning("YouTube service không khả dụng, bỏ qua việc thêm video")
            return dishes
        
        enhanced_dishes = []
        
        try:
            # Sử dụng ThreadPoolExecutor để xử lý song song
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit tất cả các task
                future_to_dish = {
                    executor.submit(self.enhance_dish_with_video, dish): dish 
                    for dish in dishes
                }
                
                # Collect kết quả
                for future in concurrent.futures.as_completed(future_to_dish):
                    try:
                        enhanced_dish = future.result(timeout=30)  # Timeout 30 giây cho mỗi dish
                        enhanced_dishes.append(enhanced_dish)
                    except concurrent.futures.TimeoutError:
                        original_dish = future_to_dish[future]
                        logger.warning(f"Timeout khi tìm video cho món '{original_dish.name}'")
                        enhanced_dishes.append(original_dish)
                    except Exception as e:
                        original_dish = future_to_dish[future]
                        logger.error(f"Lỗi khi xử lý món '{original_dish.name}': {str(e)}")
                        enhanced_dishes.append(original_dish)
        
        except Exception as e:
            logger.error(f"Lỗi khi xử lý song song: {str(e)}")
            # Fallback: xử lý tuần tự
            enhanced_dishes = [self.enhance_dish_with_video(dish) for dish in dishes]
        
        # Đảm bảo thứ tự giống như input
        enhanced_dishes.sort(key=lambda d: next(i for i, orig in enumerate(dishes) if orig.name == d.name))
        
        success_count = sum(1 for dish in enhanced_dishes if dish.video_url)
        logger.info(f"Đã thêm video thành công cho {success_count}/{len(dishes)} món ăn")
        
        return enhanced_dishes
    
    async def enhance_dishes_with_videos_async(self, dishes: List[Dish]) -> List[Dish]:
        """
        Phiên bản async của enhance_dishes_with_videos
        
        Args:
            dishes: Danh sách các món ăn cần cải thiện
            
        Returns:
            Danh sách món ăn đã được cải thiện
        """
        if not dishes:
            return dishes
        
        logger.info(f"Đang cải thiện {len(dishes)} món ăn với video URLs (async)...")
        
        # Nếu YouTube service không khả dụng, trả về danh sách gốc
        if not self.youtube_service.available:
            logger.warning("YouTube service không khả dụng, bỏ qua việc thêm video")
            return dishes
        
        # Chạy enhance_dishes_with_videos trong thread pool
        loop = asyncio.get_event_loop()
        enhanced_dishes = await loop.run_in_executor(
            None, 
            self.enhance_dishes_with_videos, 
            dishes
        )
        
        return enhanced_dishes
    
    def enhance_single_dish_name(self, dish_name: str) -> Optional[str]:
        """
        Tìm video URL cho tên món ăn (không cần đối tượng Dish)
        
        Args:
            dish_name: Tên món ăn
            
        Returns:
            Video URL hoặc None
        """
        try:
            return self.youtube_service.get_youtube_video_url(dish_name)
        except Exception as e:
            logger.error(f"Lỗi khi tìm video cho '{dish_name}': {str(e)}")
            return None

# Tạo instance global
dish_enhancement_service = DishEnhancementService()
