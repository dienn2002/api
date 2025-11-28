from enum import Enum

class MessageError(Enum):
    NOT_FOUND = ('NOT_FOUND', 'Không tồn tại')
    INVALID = ('INVALID', 'Không hợp lệ')
    STATUS_INVALID = ('STATUS_INVALID', 'Trạng Thái Không hợp lệ')
    DETECT_PLATE_NUMBER_ERROR =  ('DETECT_PLATE_NUMBER_ERROR', 'Không đọc được biển số')
    TYPE_NOT_SUPPORTED = ('TYPE_NOT_SUPPORTED', 'Type không hợp lệ')
    SERVER_ERROR = ('SERVER_ERROR', 'Có lỗi trong quá trình xử lý')

    def code(self):
        return self.value[0]
    
    def message(self):
        return self.value[1]
    
    