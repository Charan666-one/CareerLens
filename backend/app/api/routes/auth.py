from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    verify_dummy_password,
    verify_password,
)
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import RegisterResult, Token, UserLogin, UserOut, UserRegister

router = APIRouter()


@router.post("/register", response_model=RegisterResult, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        target_role=payload.target_role,
        experience_years=payload.experience_years or 0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Sign the new account in directly. Setting a password is already proof
    # of control over it, so bouncing the user to the login form to retype
    # what they just chose added a second bcrypt verify and a form round
    # trip for nothing.
    return RegisterResult(
        **UserOut.model_validate(user).model_dump(),
        access_token=create_access_token(data={"sub": str(user.id)}),
    )


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Both failure paths have to cost about the same. Short-circuiting on a
    # missing user would answer in ~7 ms while a wrong password for a real
    # account takes ~67 ms, which tells an attacker which emails have
    # accounts here. The dummy verify burns the same bcrypt time instead.
    if user is None:
        verify_dummy_password(payload.password)
        password_ok = False
    else:
        password_ok = verify_password(payload.password, user.hashed_password)

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user