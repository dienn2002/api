from fastapi import APIRouter, HTTPException
from persistences.dto.app_dto import AddUser, UpdateUser, DeleteUser, SearchUser, UserHistoryResponse
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()


@router.post("/register")
async def add_user(request: AddUser):
    return await user_service.add_user(request)

@router.put("/update")
async def update_user(request: UpdateUser):
    return await user_service.update_user(request)

@router.delete("/delete")
async def delete_user(request: DeleteUser):
    return await user_service.delete_user(request)

@router.post("/search", response_model=UserHistoryResponse)
async def search_user(request: SearchUser):
    return await user_service.search_user(request)