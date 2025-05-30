import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()

# For mock database
class MockFirestoreDB:
    """A mock Firestore database for testing"""
    def __init__(self):
        self.data = {}
        print("Using Mock Firestore Database")
    
    def collection(self, collection_name):
        if collection_name not in self.data:
            self.data[collection_name] = {}
        return MockCollection(self, collection_name)

class MockCollection:
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name
    
    def document(self, doc_id):
        return MockDocument(self.db, self.collection_name, doc_id)
    
    def where(self, filter=None):
        # Mock implementation of where query
        return MockQuery(self.db, self.collection_name)

class MockDocument:
    def __init__(self, db, collection_name, doc_id):
        self.db = db
        self.collection_name = collection_name
        self.doc_id = doc_id
        
    def get(self):
        # Create a mock document snapshot
        doc_ref = self.db.data.get(self.collection_name, {}).get(self.doc_id, None)
        return MockDocSnapshot(doc_ref, self.doc_id, exists=(doc_ref is not None))
        
    def set(self, data):
        if self.collection_name not in self.db.data:
            self.db.data[self.collection_name] = {}
        self.db.data[self.collection_name][self.doc_id] = data
        print(f"MOCK: Set document {self.collection_name}/{self.doc_id}")
        return True
        
    def update(self, data):
        if self.collection_name in self.db.data and self.doc_id in self.db.data[self.collection_name]:
            self.db.data[self.collection_name][self.doc_id].update(data)
            print(f"MOCK: Updated document {self.collection_name}/{self.doc_id}")
            return True
        return False
        
    def delete(self):
        if self.collection_name in self.db.data and self.doc_id in self.db.data[self.collection_name]:
            del self.db.data[self.collection_name][self.doc_id]
            print(f"MOCK: Deleted document {self.collection_name}/{self.doc_id}")
            return True
        return False
        
    def collection(self, subcollection_name):
        key = f"{self.collection_name}/{self.doc_id}/{subcollection_name}"
        return MockCollection(self.db, key)

class MockDocSnapshot:
    def __init__(self, data, doc_id, exists=True):
        self.data_dict = data
        self.doc_id = doc_id
        self._exists = exists
        
    def to_dict(self):
        return self.data_dict or {}
        
    @property
    def exists(self):
        return self._exists
        
    @property
    def reference(self):
        # Return self as a simple placeholder for doc reference
        return self

class MockQuery:
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name
        
    def get(self):
        # Return empty list as mock query result
        print(f"MOCK: Query on {self.collection_name} executed")
        return []
        
    def limit(self, count):
        return self

class FirebaseConfig:
    """Quản lý kết nối Firebase"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.db = None
        self.app = None
        self.initialized = False
        self.using_mock = False
        
        try:
            # Kiểm tra xem đã khởi tạo Firebase chưa
            if not firebase_admin._apps:
                credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
                
                # Kiểm tra file credentials tồn tại
                if os.path.exists(credentials_path):
                    # Khởi tạo Firebase với file credentials
                    cred = credentials.Certificate(credentials_path)
                    self.app = firebase_admin.initialize_app(cred)
                    print("Firebase initialized successfully with credentials file")
                else:
                    # Thử khởi tạo với chuỗi JSON từ biến môi trường
                    credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
                    if credentials_json:
                        try:
                            credentials_dict = json.loads(credentials_json)
                            cred = credentials.Certificate(credentials_dict)
                            self.app = firebase_admin.initialize_app(cred)
                            print("Firebase initialized successfully with credentials JSON")
                        except json.JSONDecodeError:
                            print("Error: FIREBASE_CREDENTIALS_JSON is not valid JSON")
                            # Use mock database
                            self.db = MockFirestoreDB()
                            self.initialized = True
                            self.using_mock = True
                            return
                    else:
                        print("Warning: No Firebase credentials found. Using mock database.")
                        # Use mock database
                        self.db = MockFirestoreDB()
                        self.initialized = True
                        self.using_mock = True
                        return
            else:
                self.app = firebase_admin.get_app()
                print("Using existing Firebase app")
                
            # Khởi tạo Firestore
            if not self.using_mock:
                self.db = firestore.client()
            self.initialized = True
                
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            print("Falling back to mock database")
            self.db = MockFirestoreDB()
            self.initialized = True
            self.using_mock = True
    
    def get_db(self):
        """Trả về đối tượng Firestore database"""
        if not self.initialized:
            # Initialize with mock database if not initialized
            self.db = MockFirestoreDB()
            self.initialized = True
            self.using_mock = True
        return self.db

# Tạo instance toàn cục
firebase_config = FirebaseConfig() 