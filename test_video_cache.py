#!/usr/bin/env python3
"""
Test video cache system
"""

from services.video_cache_service import video_cache_service
from youtube_service import youtube_service

def test_video_cache_system():
    """Test toàn bộ hệ thống cache video"""
    
    print("🧪 Testing Video Cache System...")
    
    # Test 1: Kiểm tra cache stats ban đầu
    print("\n📊 Test 1: Cache stats ban đầu")
    stats = video_cache_service.get_cache_stats()
    print(f"Cache stats: {stats}")
    
    # Test 2: Test cache một video thủ công
    print("\n💾 Test 2: Cache video thủ công")
    test_dish = "Phở Bò"
    test_video = "https://www.youtube.com/watch?v=test123"
    
    success = video_cache_service.cache_video(test_dish, test_video, "manual")
    print(f"Cache thành công: {success}")
    
    # Test 3: Lấy video từ cache
    print("\n🔍 Test 3: Lấy video từ cache")
    cached_video = video_cache_service.get_cached_video(test_dish)
    print(f"Video từ cache: {cached_video}")
    
    # Test 4: Test YouTube service với cache
    print("\n🎥 Test 4: YouTube service với cache")
    test_dishes = ["Phở Bò", "Cơm Gà", "Bánh Mì", "Bún Bò Huế"]
    
    for dish in test_dishes:
        print(f"\nTesting: {dish}")
        video_url = youtube_service.get_youtube_video_url(dish)
        if video_url:
            print(f"  ✅ Video: {video_url}")
        else:
            print(f"  ❌ Không có video")
    
    # Test 5: Kiểm tra cache stats sau khi test
    print("\n📊 Test 5: Cache stats sau test")
    final_stats = video_cache_service.get_cache_stats()
    print(f"Final cache stats: {final_stats}")
    
    # Test 6: Test lại để xem có sử dụng cache không
    print("\n🔄 Test 6: Test lại để kiểm tra cache")
    for dish in test_dishes[:2]:  # Chỉ test 2 món đầu
        print(f"\nTesting lại: {dish}")
        video_url = youtube_service.get_youtube_video_url(dish)
        if video_url:
            print(f"  ✅ Video (should be from cache): {video_url}")
        else:
            print(f"  ❌ Không có video")

if __name__ == "__main__":
    test_video_cache_system()
