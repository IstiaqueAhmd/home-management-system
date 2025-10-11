from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class HomeBase(BaseModel):
    name: str
    description: Optional[str] = None

class HomeCreate(HomeBase):
    pass

class Home(HomeBase):
    id: Optional[str] = None
    leader_username: str
    members: List[str] = []
    date_created: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    is_active: bool = True
    home_id: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str

class User(UserBase):
    id: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class ContributionCreate(BaseModel):
    product_name: str
    amount: float
    description: Optional[str] = None

class Contribution(BaseModel):
    id: Optional[str] = None
    username: str
    home_id: str
    product_name: str
    amount: float
    description: Optional[str] = None
    date_created: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TransferCreate(BaseModel):
    recipient_username: str
    amount: float
    description: Optional[str] = None

class Transfer(BaseModel):
    id: Optional[str] = None
    sender_username: str
    recipient_username: str
    home_id: str
    amount: float
    description: Optional[str] = None
    date_created: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
