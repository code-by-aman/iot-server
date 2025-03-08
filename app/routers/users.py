from fastapi import APIRouter, Depends, HTTPException, status, Request
from bson.objectid import ObjectId
from app.database import user_collection
from app.schemas import UserResponse, UpdateUser
from app.routers.auth import get_current_user
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/api/users", tags=["Users"])

# Helper function to fetch user by ID
def get_user_by_id(user_id: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])  # Convert ObjectId to string for JSON serialization
    return user

# API to get details of the currently authenticated user
@router.get("/me", response_model=UserResponse)
def get_my_details(user=Depends(get_current_user)):
    return user

# API to get user details by ID (restricted to superusers)
@router.get("/{user_id}", response_model=UserResponse)
def get_user_details(user_id: str, current_user=Depends(get_current_user)):
    # Ensure the current user is a superuser
    if not current_user["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/update/{user_id}")
async def update_user(user_id: str, req_data: UpdateUser, current_user=Depends(get_current_user)):
    user_data = req_data.dict()
    user = get_user_by_id(user_id)
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    for key in user_data.keys():
        user[key] = user_data[key]

    del user["id"]
    print("user", user)
    user_collection.find_one_and_update({"_id": ObjectId(user_id)}, {"$set": user}, upsert=False)
    return {"message": "User updated successfully"}

@router.put("/admin/update/{user_id}")
async def update_user(user_id: str, req_data: UpdateUser, current_user=Depends(get_current_user)):
    user_data = req_data.dict()
    user = get_user_by_id(user_id)
    if not current_user["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    for key in user_data.keys():
        user[key] = user_data[key]

    del user["id"]
    print("user", user)
    user_collection.find_one_and_update({"_id": ObjectId(user_id)}, {"$set": user}, upsert=False)
    return {"message": "User updated successfully"}

@router.get("/admin/user-list", response_model=List[UserResponse])
async def get_users_list(current_user=Depends(get_current_user)):
    if not current_user["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    user_list = list(user_collection.find())
    for user in user_list:
        user["id"] = str(user["_id"])
        del user["_id"]
    print('user_list..............', user_list)
    return user_list