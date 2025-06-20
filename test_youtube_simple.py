import requests
import json

def test_youtube_search():
    """Test YouTube search endpoint"""
    print("🔍 Testing YouTube search endpoint...")
    
    url = 'http://localhost:8000/youtube/search'
    data = {
        'query': 'Phở Bò',
        'max_results': 3,
        'duration': 'medium',
        'order': 'relevance'
    }
    
    try:
        print(f"📡 Making request to: {url}")
        response = requests.post(url, json=data, timeout=30)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            videos = result.get('videos', [])
            cached = result.get('cached', False)
            
            print(f"✅ Found {len(videos)} videos")
            print(f"📦 Cached: {cached}")
            
            for i, video in enumerate(videos[:2]):
                title = video.get('title', 'No title')
                duration = video.get('duration', 'N/A')
                views = video.get('views', 'N/A')
                
                print(f"{i+1}. {title}")
                print(f"   Duration: {duration} | Views: {views}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_youtube_search()
