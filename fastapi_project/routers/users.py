from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from sqlmodel import select
from ..database import User, SessionDP
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv("ACCES_TOKEN_EXPIRE_MINUTES")



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDP):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = session.exec(select(User).where(User.username==username)).first()
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
def register(username: str, password: str, session: SessionDP):
    user = session.exec(select(User).where(User.username==username)).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"msg": "User registered successfully"}

@user_router.post("/login")
async def login(username: str, password: str, session: SessionDP):
    user = session.exec(select(User).where(User.username==username)).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)))
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/users/me")
async def read_users_me(current_user: Annotated[str, Depends(get_current_user)]):
    return {"username": current_user}