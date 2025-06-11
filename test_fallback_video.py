#!/usr/bin/env python3
"""
Test fallback video system
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from youtube_service import YouTubeService
    
    # Create service instance
    youtube_service = YouTubeService()
    
    # Test fallback videos
    test_dishes = ['Cơm Gà Xối', 'Bánh Mì Chay', 'Phở Bò', 'Bún Thịt Nướng', 'Canh Chua']
    
    print('🧪 Test fallback videos...')
    print(f'YouTube API available: {youtube_service.available}')
    print(f'Fallback videos count: {len(youtube_service.fallback_videos)}')
    
    for dish in test_dishes:
        print(f'\nTesting: {dish}')
        try:
            video_url = youtube_service.get_youtube_video_url(dish)
            if video_url:
                print(f'  ✅ Video: {video_url}')
            else:
                print(f'  ❌ Không có video')
        except Exception as e:
            print(f'  ❌ Error: {e}')
            
except Exception as e:
    print(f'❌ Import error: {e}')
    import traceback
    traceback.print_exc()
