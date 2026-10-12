from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    name: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = 0


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: str
    name: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResult(UserOut):
    """What POST /api/auth/register returns: the new user, plus a token.

    Registering already proves the caller controls the credentials, so
    making them sign in again right afterwards bought nothing and cost a
    second bcrypt verify plus a round trip through the login form. The
    token is issued the same way login issues it, with the same expiry.

    This extends UserOut rather than replacing it, so every field the
    endpoint returned before is still there - only the two token fields
    are new.
    """

    access_token: str
    token_type: str = "bearer"