from datetime import timezone, datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from sqlmodel import select
from fastapi_project.database import User, SessionDP, UserRead, UserRegister
from fastapi_project.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDP):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await session.execute(select(User).where(User.username==username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(id: int, session: SessionDP) -> User:
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.post("/register")
async def register(user: UserRegister, session: SessionDP):
    result = await session.execute(select(User).where(User.username==user.username))
    old_user = result.scalars().first()
    if old_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"msg": "User registered successfully"}

@user_router.post("/login")
async def login(user: UserRegister, session: SessionDP):
    result = await session.execute(select(User).where(User.username==user.username))
    login_user = result.scalars().first()
    if not login_user or not verify_password(user.password, login_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)))
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/users/me")
async def read_users_me(session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]):
    result = await get_user(current_user, session)
    user = UserRead.from_orm(result)
    return user