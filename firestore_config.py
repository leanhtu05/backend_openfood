import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from typing import Dict, List, Any, Optional

# Sử dụng Mock Firestore khi không có config Firebase
class MockFirestoreDatabase:
    """Mock Database cho Firestore khi không có Firebase credentials"""
    
    def __init__(self):
        print("Using Mock Firestore Database")
        self.collections = {}
        
    def collection(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]
        
class MockCollection:
    """Mock Collection cho Firestore"""
    
    def __init__(self, name):
        self.name = name
        self.documents = {}
        
    def document(self, id=None):
        if id is None:
            # Generate a random ID
            import uuid
            id = str(uuid.uuid4())
        
        if id not in self.documents:
            self.documents[id] = MockDocument(id, self)
            
        return self.documents[id]
        
    def where(self, field, op, value):
        return MockQuery(self, filters=[(field, op, value)])
        
    def order_by(self, field, direction=None):
        return MockQuery(self, order=(field, direction))
        
    def limit(self, limit_val):
        return MockQuery(self, limit_val=limit_val)
        
    def get(self):
        return list(self.documents.values())
        
class MockDocument:
    """Mock Document cho Firestore"""
    
    def __init__(self, id, collection):
        self.id = id
        self.collection = collection
        self.data = {}
        self.exists = False
        
    def set(self, data):
        self.data = data
        self.exists = True
        print(f"MOCK: Set document {self.collection.name}/{self.id}")
        return self
        
    def update(self, data):
        if not self.exists:
            print(f"MOCK: Document {self.collection.name}/{self.id} does not exist.")
            return self
            
        for key, value in data.items():
            self.data[key] = value
            
        print(f"MOCK: Updated document {self.collection.name}/{self.id}")
        return self
        
    def get(self):
        return self
        
    def delete(self):
        if self.id in self.collection.documents:
            del self.collection.documents[self.id]
            print(f"MOCK: Deleted document {self.collection.name}/{self.id}")
        
    def to_dict(self):
        return self.data
        
    @property
    def reference(self):
        return self
        
class MockQuery:
    """Mock Query cho Firestore"""
    
    def __init__(self, collection, filters=None, order=None, limit_val=None):
        self.collection = collection
        self.filters = filters or []
        self.order_params = order
        self.limit_val = limit_val
        
    def where(self, field, op, value):
        new_filters = self.filters + [(field, op, value)]
        return MockQuery(self.collection, filters=new_filters, order=self.order_params, limit_val=self.limit_val)
        
    def order_by(self, field, direction=None):
        return MockQuery(self.collection, filters=self.filters, order=(field, direction), limit_val=self.limit_val)
        
    def limit(self, limit_val):
        return MockQuery(self.collection, filters=self.filters, order=self.order_params, limit_val=limit_val)
        
    def stream(self):
        """Simulate Firestore stream by filtering documents"""
        documents = list(self.collection.documents.values())
        
        # Apply filters
        for field, op, value in self.filters:
            if op == '==':
                documents = [doc for doc in documents if field in doc.data and doc.data[field] == value]
                
        # Apply limit
        if self.limit_val is not None and self.limit_val < len(documents):
            documents = documents[:self.limit_val]
            
        return documents
        
    def get(self):
        return self.stream()

class FirebaseConfig:
    """Firebase configuration singleton"""
    
    def __init__(self):
        self.app = None
        self.db = None
        self.credentials_path = os.environ.get("FIREBASE_CREDENTIALS", "firebase-credentials.json")
        self.initialized = False
        self._init_firebase()
        
    def _init_firebase(self):
        """Initialize Firebase"""
        if firebase_admin._apps:
            # Already initialized
            self.app = firebase_admin._apps[0]
            self.db = firestore.client()
            self.initialized = True
            print("Firebase already initialized")
            return
            
        try:
            if os.path.exists(self.credentials_path):
                print(f"Firebase initialized successfully with credentials file")
                cred = credentials.Certificate(self.credentials_path)
                self.app = firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
            else:
                print(f"Warning: No Firebase credentials found. Using mock database.")
                self.db = MockFirestoreDatabase()
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            self.db = MockFirestoreDatabase()
            
    def get_db(self):
        """Get Firestore database client"""
        return self.db
        
# Singleton instance
firebase_config = FirebaseConfig() 