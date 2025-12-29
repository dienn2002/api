from configs.db_config import session_scope
from repository.history_repository import HistoryRepository
from persistences.dto.app_dto import UserHistoryResponse, HistoryItem, LastestInOutResponse
from utils.common_utils import format_db_time
from constants.message_error import MessageError
# from persistences.entitys.history import History

class HistoryService:
    def __init__(self):
        self.history_repo = HistoryRepository()

    async def all_history(self):
            try:
                with session_scope() as session:
                    histories = self.history_repo.get_all_history(session)
                    history_list = [HistoryItem(id=h.id, plate_number=h.plate_number, status=h.status, count=h.count, created_at=format_db_time(h.created_at)) for h in histories]
                    return UserHistoryResponse(is_success=True, history=history_list, count=len(history_list))
            except Exception as e:
                return UserHistoryResponse(is_success=False, error_code=MessageError.SERVER_ERROR.code(), error_message=str(e), history=[], count=0)
            


    # async def get_latest_in_out(self, plate_number: str):
    #     try:
    #         with session_scope() as session:
    #             result =  self.history_repo.get_latest_in_out(session, plate_number)

    #             if not result:
    #                 response = LastestInOutResponse(
    #                     is_success=False,
    #                     plate_number=plate_number,
    #                     time_in=None,
    #                     time_out=None,
    #                     tong_thoi_gian=0,
    #                     so_tien=0,
    #                     error_code=MessageError.HISTORY_NOT_FOUND.code(),
    #                     error_message=MessageError.HISTORY_NOT_FOUND.message()
    #                 )
    #             else:
    #                 so_tien = calculate_fee(result["time_in"], result["time_out"])
    #                 tong_thoi_gian = int((result["time_out"] - result["time_in"]).total_seconds() / 3600)
                    
    #                 response = LastestInOutResponse(
    #                     is_success=True,
    #                     plate_number=plate_number,
    #                     time_in=format_db_time(result["time_in"]),
    #                     time_out=format_db_time(result["time_out"]),
    #                     tong_thoi_gian = tong_thoi_gian,
    #                     so_tien = so_tien
    #                 )
    #             print("[HISTORY] [GET LASTEST IN OUT] response: " , response)
    #             return response
            
    #     except Exception as e:
    #         print("[HISTORY] [ERROR]:", str(e))
    #         return LastestInOutResponse(
    #             is_success=False,
    #             error_code=MessageError.SERVER_ERROR.code(),
    #             error_message=str(e)
    #         )

    
