from pydantic import BaseModel, Field
from typing import Optional, List

class TDEEValues(BaseModel):
    calories: Optional[int]
    carbs: Optional[int]
    fat: Optional[int]
    protein: Optional[int]

class FlutterUserProfile(BaseModel):
    activityLevel: Optional[str]
    age: Optional[int]
    createdAt: Optional[str]  # hoặc datetime nếu muốn parse
    dietPreference: Optional[str]
    dietRestrictions: Optional[List[str]]
    displayName: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    goal: Optional[str]
    healthConditions: Optional[List[str]]
    heightCm: Optional[float]
    isAnonymous: Optional[bool]
    isStructureSample: Optional[bool]
    lastLoginAt: Optional[str]
    photoURL: Optional[str]
    tdeeValues: Optional[TDEEValues]
    uid: Optional[str]
    weightKg: Optional[float]
    
    def to_dict(self):
        """Convert the model to a dictionary for Firestore"""
        data = {k: v for k, v in self.dict().items() if v is not None}
        
        # Convert nested TDEEValues to dict if exists
        if self.tdeeValues:
            data["tdeeValues"] = self.tdeeValues.dict()
            
        return data
        
    def dict(self, *args, **kwargs):
        """Override dict method to handle nested objects"""
        result = super().dict(*args, **kwargs)
        
        # Make sure nested objects are properly converted
        if self.tdeeValues:
            result["tdeeValues"] = self.tdeeValues.dict(*args, **kwargs)
            
        return result

class FlutterUserUpdate(BaseModel):
    """Model cho dữ liệu cập nhật từ Flutter"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    activityLevel: Optional[str] = None
    dietType: Optional[str] = None
    preferred_cuisines: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    tdeeValues: Optional[TDEEValues] = None
    heightCm: Optional[float] = None
    weightKg: Optional[float] = None
    
    def to_dict(self):
        """Convert the model to a dictionary for Firestore"""
        data = {k: v for k, v in self.dict().items() if v is not None}
        
        # Chuyển đổi các trường từ Flutter sang định dạng Firestore
        if self.heightCm is not None and "height" not in data:
            data["height"] = self.heightCm
            
        if self.weightKg is not None and "weight" not in data:
            data["weight"] = self.weightKg
            
        # Convert nested TDEEValues to dict if exists
        if self.tdeeValues:
            data["tdeeValues"] = self.tdeeValues.dict()
            
        return data 