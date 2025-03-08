from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.utils.utils import verify_password, hash_password, create_access_token
from app.schemas import UserRequest, Token, UserResponse
from app.config import settings
from app.database import user_collection
from bson import ObjectId
from fastapi import Body

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def get_user(user_id: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
    return user

def get_user_from_username(username: str):
    return user_collection.find_one({"username": username})

def authenticate_user(username: str, password: str):
    user = get_user_from_username(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

@router.post("/register")
def register(user: UserRequest):
    if get_user_from_username(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user_data = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "device_id": None,  # Optional; can be assigned later
        "is_active": True,
        "is_superuser": False,
        "name": user.name,
        "email": user.email,
        "number": user.number,
    }
    print('user_data', user_data)
    user_collection.insert_one(user_data)
    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["username"], "id": str(user["_id"])},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Create refresh token with longer expiration
    refresh_token = create_access_token(
        data={"sub": user["username"], "id": str(user["_id"]), "refresh": True},
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str = Body(..., embed=True)):
    try:
        print('refresh_token', refresh_token)
        # Decode the refresh token
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print('payload', payload)
        
        # Verify this is a refresh token
        if not payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
            
        user_id = payload.get("id")
        username = payload.get("sub")
        
        # Generate new tokens
        access_token = create_access_token(
            data={"sub": username, "id": user_id},
            expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        refresh_token = create_access_token(
            data={"sub": username, "id": user_id, "refresh": True},
            expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = get_user(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
