"""
Firebase Storage service for handling image uploads
"""
import os
import time
from datetime import datetime
from typing import Optional
import uuid

try:
    import firebase_admin
    from firebase_admin import storage
    FIREBASE_STORAGE_AVAILABLE = True
except ImportError:
    print("Firebase Admin SDK not installed. Use 'pip install firebase-admin'")
    FIREBASE_STORAGE_AVAILABLE = False

class FirebaseStorageService:
    """Service for handling file operations with Firebase Storage"""
    
    def __init__(self, bucket_name=None):
        """Initialize Firebase Storage service"""
        self.available = FIREBASE_STORAGE_AVAILABLE
        self.bucket_name = bucket_name
        
        # Try to get Firebase app and bucket
        try:
            # Get bucket from existing Firebase app
            if self.bucket_name:
                self.bucket = storage.bucket(name=self.bucket_name)
            else:
                self.bucket = storage.bucket()
                
            self.bucket_name = self.bucket.name
            print(f"Firebase Storage service initialized with bucket: {self.bucket.name}")
            self.available = True
        except Exception as e:
            print(f"Error initializing Firebase Storage service: {str(e)}")
            self.available = False
            self.bucket = None
    
    def check_connection(self) -> bool:
        """
        Check if connection to Firebase Storage is working
        
        Returns:
            True if connection is working, False otherwise
        """
        if not self.available or not self.bucket:
            return False
            
        try:
            # Try to list files to check if connection is working
            blobs = list(self.bucket.list_blobs(max_results=1))
            print(f"Successfully connected to Firebase Storage bucket: {self.bucket.name}")
            return True
        except Exception as e:
            print(f"Error connecting to Firebase Storage: {str(e)}")
            self.available = False
            return False
            
    def upload_image(self, 
                    image_data: bytes, 
                    user_id: str, 
                    folder: str = "food_images",
                    content_type: str = "image/jpeg") -> Optional[str]:
        """
        Upload an image to Firebase Storage
        
        Args:
            image_data: Raw image data
            user_id: User ID to include in path
            folder: Storage folder name
            content_type: Image MIME type
            
        Returns:
            Public URL of the uploaded image or None if upload failed
        """
        if not self.available or not self.bucket:
            print("Firebase Storage is not available")
            return None
            
        try:
            # Generate unique filename
            timestamp = int(time.time() * 1000)
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{timestamp}_{unique_id}.jpg"
            
            # Create path with user ID for organization
            path = f"{folder}/{user_id}/{filename}"
            
            # Create blob and upload data
            blob = self.bucket.blob(path)
            blob.upload_from_string(image_data, content_type=content_type)
            
            # Make image publicly accessible
            blob.make_public()
            
            # Return public URL
            image_url = blob.public_url
            print(f"Image uploaded successfully to: {image_url}")
            
            return image_url
        except Exception as e:
            print(f"Error uploading image to Firebase Storage: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from Firebase Storage using its URL
        
        Args:
            image_url: Public URL of the image to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.available or not self.bucket:
            print("Firebase Storage is not available")
            return False
            
        try:
            # Extract path from URL
            # Format: https://storage.googleapis.com/BUCKET_NAME/PATH
            bucket_name = self.bucket.name
            path = image_url.split(f"{bucket_name}/")[1]
            
            # Delete blob
            blob = self.bucket.blob(path)
            blob.delete()
            
            print(f"Image deleted successfully: {path}")
            return True
        except Exception as e:
            print(f"Error deleting image from Firebase Storage: {str(e)}")
            return False
            
    def list_files(self, prefix: str = None, max_results: int = 100) -> list:
        """
        List files in Firebase Storage
        
        Args:
            prefix: Filter results to objects whose names begin with this prefix
            max_results: Maximum number of results to return
            
        Returns:
            List of file names
        """
        if not self.available or not self.bucket:
            print("Firebase Storage is not available")
            return []
            
        try:
            blobs = list(self.bucket.list_blobs(prefix=prefix, max_results=max_results))
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listing files in Firebase Storage: {str(e)}")
            return []

# Create singleton instance with bucket name from config
from config import FIREBASE_STORAGE_BUCKET
firebase_storage_service = FirebaseStorageService(bucket_name=FIREBASE_STORAGE_BUCKET) 