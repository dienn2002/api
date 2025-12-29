from fastapi import APIRouter, Query
from persistences.dto.app_dto import UserHistoryResponse
from services.history_service import HistoryService


router = APIRouter(prefix="/history", tags=["History"])
history_service = HistoryService()

@router.get("/all-history", response_model=UserHistoryResponse)
async def get_all_history():
    return await history_service.all_history()

