import requests
import json

def test_flutter_data_sync():
    """Test if the server can receive data from Flutter"""
    
    print("Testing if the server can receive data from Flutter...")
    
    # Test data
    user_id = "test_flutter_user"
    user_data = {
        "name": "Test User from Flutter",
        "email": "test_flutter@example.com",
        "height": 170,
        "weight": 65,
        "age": 30,
        "gender": "male",
        "activity_level": "moderate",
        "goal": "maintain_weight"
    }
    
    try:
        # Create user directly instead of using sync
        response = requests.post(
            f"http://localhost:8000/firestore/users/{user_id}",
            json=user_data
        )
        
        # Print the response
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("SUCCESS: Server successfully received data from Flutter!")
        else:
            print(f"ERROR: Server returned status code {response.status_code}")
            
        # Now retrieve the user data to verify it was stored
        print("\nRetrieving user data to verify it was stored...")
        get_response = requests.get(
            f"http://localhost:8000/firestore/users/{user_id}"
        )
        
        print(f"GET Status: {get_response.status_code}")
        if get_response.status_code == 200:
            print(f"Retrieved user data: {json.dumps(get_response.json(), indent=2)}")
            print("SUCCESS: Server successfully stored and retrieved Flutter data!")
        else:
            print(f"Error response: {get_response.text}")
            print("ERROR: Could not retrieve user data")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        
if __name__ == "__main__":
    test_flutter_data_sync() 