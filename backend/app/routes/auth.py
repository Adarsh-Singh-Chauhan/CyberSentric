"""
CyberSentric Auth Routes
JWT-based authentication with role-based access control.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from jose import JWTError, jwt
import bcrypt
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        return False

# In-memory user store (replace with PostgreSQL in production)
USERS_DB: dict[str, dict] = {
    "admin": {"username": "admin", "password": hash_password("admin123"),
              "role": "admin", "created": datetime.utcnow().isoformat()},
    "user": {"username": "user", "password": hash_password("user123"),
             "role": "user", "created": datetime.utcnow().isoformat()},
}


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    if not creds:
        return {"username": "anonymous", "role": "user"}
    try:
        payload = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username and username in USERS_DB:
            return {"username": username, "role": USERS_DB[username]["role"]}
    except JWTError:
        pass
    return {"username": "anonymous", "role": "user"}


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = USERS_DB.get(req.username)
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": req.username, "role": user["role"]})
    return TokenResponse(access_token=token, role=user["role"], username=req.username)


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    if req.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    USERS_DB[req.username] = {
        "username": req.username, "password": hash_password(req.password),
        "role": req.role if req.role in ("admin", "user") else "user",
        "created": datetime.utcnow().isoformat(),
    }
    token = create_token({"sub": req.username, "role": USERS_DB[req.username]["role"]})
    return TokenResponse(access_token=token, role=USERS_DB[req.username]["role"], username=req.username)


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user
