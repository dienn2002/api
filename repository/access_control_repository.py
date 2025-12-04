from configs.db_config import session_scope
from repository.user_repository import UserRepository
from repository.history_repository import HistoryRepository
from models.schemas.access_schema import AccessControlResponse, BaseResponse
from utils.plate_utils import retrieve_plate_number
from utils.time_utils import format_db_time
from utils.consts import IN, OUT
from constants.message_error import MessageError
from models.tables.history_model import History

class AccessControlService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.history_repo = HistoryRepository()

    async def process_request(self, request):
        if not request or not validate_type(request.type):
            return AccessControlResponse(
                is_success=False,
                error_code=MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message=MessageError.TYPE_NOT_SUPPORTED.message()
            )

        plate_number = retrieve_plate_number(request.plate_image)
        if not plate_number:
            return AccessControlResponse(
                is_success=False,
                error_code=MessageError.DETECT_PLATE_NUMBER_ERROR.code(),
                error_message=MessageError.DETECT_PLATE_NUMBER_ERROR.message()
            )

        with session_scope() as session:
            user = self.user_repo.get_by_plate_number(session, plate_number)
            if user:
                if user.status == request.type.upper():
                    return AccessControlResponse(
                        is_success=False,
                        plate_number=plate_number,
                        face_image=user.face_image,
                        error_code=MessageError.STATUS_INVALID.code(),
                        error_message=MessageError.STATUS_INVALID.message(),
                        full_name=user.full_name
                    )
                else:
                    count = self.history_repo.count_by_plate_and_status(session, plate_number, IN)
                    return AccessControlResponse(
                        is_success=True,
                        plate_number=plate_number,
                        face_image=user.face_image,
                        update_time=format_db_time(user.update_at),
                        count=count,
                        full_name=user.full_name
                    )
            else:
                return AccessControlResponse(
                    is_success=False,
                    plate_number=plate_number,
                    error_code=MessageError.NOT_FOUND.code(),
                    error_message=MessageError.NOT_FOUND.message()
                )

    async def verify_backup(self, request):
        if not request or not validate_type(request.approval_type):
            return AccessControlResponse(
                is_success=False,
                error_code=MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message=MessageError.TYPE_NOT_SUPPORTED.message()
            )
        with session_scope() as session:
            new_hist = History(
                plate_number=request.plate_number,
                plate_image=request.plate_image,
                face_image="Xác nhận bởi Nhân Viên",
                status=request.approval_type,
                count=self.history_repo.max_count_for_plate(session, request.plate_number, request.approval_type) + 1
            )
            self.history_repo.create_history(session, new_hist)
            self.user_repo.update_status(session, request.plate_number, request.approval_type)
        return BaseResponse(is_success=True)

    async def process_success(self, request):
        if not request or not validate_type(request.approval_type):
            return AccessControlResponse(
                is_success=False,
                error_code=MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message=MessageError.TYPE_NOT_SUPPORTED.message()
            )
        with session_scope() as session:
            new_hist = History(
                plate_number=request.plate_number,
                face_image=request.face_image,
                plate_image=request.plate_image,
                status=request.approval_type,
                count=self.history_repo.max_count_for_plate(session, request.plate_number, request.approval_type) + 1
            )
            self.history_repo.create_history(session, new_hist)
            self.user_repo.update_status(session, request.plate_number, request.approval_type)
        return BaseResponse(is_success=True)

    async def check_plate_number(self, request):
        if not request or not validate_type(request.request_type):
            return AccessControlResponse(
                is_success=False,
                error_code=MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message=MessageError.TYPE_NOT_SUPPORTED.message()
            )
        with session_scope() as session:
            user = self.user_repo.get_by_plate_number(session, request.plate_number)
            if user:
                if user.status == request.request_type.upper():
                    return AccessControlResponse(
                        is_success=False,
                        plate_number=request.plate_number,
                        face_image=user.face_image,
                        error_code=MessageError.STATUS_INVALID.code(),
                        error_message=MessageError.STATUS_INVALID.message(),
                        full_name=user.full_name
                    )
                else:
                    count = self.history_repo.count_by_plate_and_status(session, request.plate_number, IN)
                    return AccessControlResponse(
                        is_success=True,
                        plate_number=request.plate_number,
                        face_image=user.face_image,
                        update_time=format_db_time(user.update_at),
                        count=count,
                        full_name=user.full_name
                    )
            else:
                return AccessControlResponse(
                    is_success=False,
                    plate_number=request.plate_number,
                    error_code=MessageError.NOT_FOUND.code(),
                    error_message=MessageError.NOT_FOUND.message()
                )

# helper
def validate_type(t: str) -> bool:
    return t in (IN, OUT)
