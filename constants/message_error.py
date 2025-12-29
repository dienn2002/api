from enum import Enum

class MessageError(Enum):
    NOT_FOUND = ('NOT_FOUND', 'Không tồn tại')
    INVALID = ('INVALID', 'Không hợp lệ')
    STATUS_INVALID = ('STATUS_INVALID', 'Trạng Thái Không hợp lệ')
    DETECT_PLATE_NUMBER_ERROR =  ('DETECT_PLATE_NUMBER_ERROR', 'Không đọc được biển số')
    TYPE_NOT_SUPPORTED = ('TYPE_NOT_SUPPORTED', 'Type không hợp lệ')
    SERVER_ERROR = ('SERVER_ERROR', 'Có lỗi trong quá trình xử lý')
    USER_ALREADY_EXISTS = ('USER_ALREADY_EXISTS', 'Người dùng đã tồn tại')
    NO_DATA_TO_UPDATE = ('NO_DATA_TO_UPDATE', 'Không có dữ liệu để cập nhật')
    UNKNOWN = ('UNKNOWN', 'Lỗi không xác định')
    HISTORY_NOT_FOUND = ('HISTORY_NOT_FOUND', 'Không tìm thấy lịch sử IN/OUT')

    def code(self):
        return self.value[0]
    
    def message(self):
        return self.value[1]
    
    