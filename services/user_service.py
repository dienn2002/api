from urllib import response
from configs.db_config import session_scope
from constants.constant import OUT
from repository.user_repository import UserRepository
from repository.history_repository import HistoryRepository
from persistences.dto.app_dto import UserResponse, UserItem, UserHistoryResponse, HistoryItem
from persistences.entitys.users import User
from utils.common_utils import format_db_time
from constants.message_error import MessageError
from helpers.ai_helper import AIHelper

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.history_repo = HistoryRepository()

    async def add_user(self, request):
        try:
            # print("[REGISTER] Request: ", request)
            with session_scope() as session:
                exists = self.user_repo.get_by_plate_number(session, request.plate_number)
                if exists:
                    response = UserResponse(
                        is_success=False,
                        plate_number=request.plate_number,
                        error_code=MessageError.USER_ALREADY_EXISTS.code(),
                        error_message=MessageError.USER_ALREADY_EXISTS.message()
                    )
                elif request.plate_number != AIHelper.retrieve_plate_number_from_base64(request.plate_image):
                    response = UserResponse(
                        is_success=False,
                        plate_number=request.plate_number,
                        error_code=MessageError.DETECT_PLATE_NUMBER_ERROR.code(),
                        error_message=MessageError.DETECT_PLATE_NUMBER_ERROR.message()
                    )
                else:
                    new_user = User(**request.dict())
                    new_user.status = OUT  # Default status
                    self.user_repo.add_user(session, new_user)

                    response = UserResponse(
                        is_success=True,
                        full_name=new_user.full_name,
                        plate_number=new_user.plate_number,
                        phone_number=new_user.phone_number,
                        created_at=format_db_time(new_user.created_at)
                    )

                print("[REGISTER] Response: ", response)
                return response

        except Exception as e:
            print("[REGISTER] [ERROR]: ", str(e))
            return UserResponse(is_success=False, error_code=MessageError.SERVER_ERROR.code(), error_message=str(e))


    async def update_user(self, request):
        try:
            print("[UPDATE USER] Request: ", request)
            # if not request or not request.plate_number:
            #     return UserResponse(is_success=False, error_code=MessageError.INVALID_INPUT.code(), error_message=MessageError.INVALID_INPUT.message())
            with session_scope() as session:
                user = self.user_repo.get_by_plate_number(session, request.plate_number)
                if not user:
                    response = UserResponse(is_success=False, plate_number=request.plate_number, error_code=MessageError.NOT_FOUND.code(), error_message=MessageError.NOT_FOUND.message())
                    print("[UPDATE USER] Response: ", response)
                    return response
                # if request.plate_number and request.plate_number != AIHelper.retrieve_plate_number_from_base64(request.plate_image):
                #     response = UserResponse(
                #         is_success=False,
                #         plate_number=request.plate_number,
                #         error_code=MessageError.DETECT_PLATE_NUMBER_ERROR.code(),
                #         error_message=MessageError.DETECT_PLATE_NUMBER_ERROR.message()
                #     )
                #     print("[UPDATE USER] Response: ", response)
                update_fields = {k: v for k, v in request.dict().items() if v is not None and k != "plate_number"}
                
                # Cần handle thêm trường hợp không có dữ liệu cập nhật
                if not update_fields:
                    response = UserResponse(
                        is_success=False,
                        plate_number=request.plate_number,
                        error_code=MessageError.NO_DATA_TO_UPDATE.code(),
                        error_message=MessageError.NO_DATA_TO_UPDATE.message()
                    )
                    print("[UPDATE USER] Response: ", response) 
                    return response

                updated = self.user_repo.update_user(session, request.plate_number, update_fields)
                response =  UserResponse(is_success=True, plate_number=updated.plate_number, full_name=updated.full_name, phone_number=updated.phone_number, created_at=format_db_time(updated.update_at))
                print("[UPDATE USER] Response: ", response)    
                return response
        except Exception as e:
            print("[UPDATE USER] [ERROR]: ", str(e))
            return UserResponse(is_success=False, error_code=MessageError.SERVER_ERROR.code(), error_message=str(e))



    async def delete_user(self, request):
        try:
            # if not request or not request.plate_number:
            #     return UserResponse(is_success=False, error_code=MessageError.INVALID_INPUT.code(), error_message=MessageError.INVALID_INPUT.message())
            
            with session_scope() as session:
                plate_number = request.plate_number.strip()
                self.history_repo.delete_by_plate_number(session, plate_number)
                deleted = self.user_repo.delete_user(session, plate_number)
                if not deleted:
                    response = UserResponse(
                        is_success=False, 
                        plate_number=plate_number, 
                        error_code=MessageError.NOT_FOUND.code(), 
                        error_message=MessageError.NOT_FOUND.message())
                    print("[DELETE USER] Response: ", response)
                    return response
                
                response = UserResponse(
                    is_success=True, 
                    plate_number=plate_number)
                print("[DELETE USER] Response: ", response)
                return response
        except Exception as e:
            print("[DELETE USER] [ERROR]: ", str(e))
            return UserResponse(
                is_success=False, 
                error_code=MessageError.UNKNOWN.code(), 
                error_message=str(e))

    async def search_user(self, request):
        try:
            # if not request or not request.plate_number:
            #     return UserHistoryResponse(is_success=False, error_code=MessageError.INVALID_DATA.code(), error_message=MessageError.INVALID_DATA.message(), history=[], count=0)
            with session_scope() as session:
                user = self.user_repo.get_by_plate_number(session, request.plate_number)

                if not user:
                    return UserHistoryResponse(
                        is_success=False, 
                        error_code=MessageError.NOT_FOUND.code(), 
                        error_message=MessageError.NOT_FOUND.message(), 
                        history=[], count=0)
             
                histories = self.history_repo.get_by_plate_number(session, request.plate_number)
                history_list = [
                    HistoryItem(
                        id=h.id, 
                        plate_number=h.plate_number, 
                        status=h.status, 
                        count=h.count, 
                        created_at=format_db_time(h.created_at)
                        )
                        for h in histories]
                user_item = UserItem(
                    plate_number=user.plate_number, 
                    full_name=user.full_name, 
                    email=user.email, 
                    phone_number=user.phone_number, 
                    status=user.status, 
                    face_image=user.face_image, 
                    plate_image=user.plate_image)
                response = UserHistoryResponse(
                    is_success=True, 
                    user=user_item, 
                    history=history_list, 
                    update_time=format_db_time(user.update_at or user.created_at), 
                    count=self.history_repo.count_by_plate_and_status(session, request.plate_number, "IN"))
                print("[SEARCH USER] Response: ", response)
                return response
        except Exception as e:
            print("[SEARCH USER] [ERROR]: ", str(e))
            return UserHistoryResponse(is_success=False, error_code=MessageError.SERVER_ERROR.code(), error_message=str(e), history=[], count=0)


    