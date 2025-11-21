import enum

class MessageError(enum.Enum):
    def __init__(self, code, message):
        self._value_ = code
        self.code = code
        self.message = message
        
    NOT_FOUND = ('NOT_FOUND', 'Người dùng không tồn tại.')
    NOT_SUPPORTED = ('NOT_SUPPORTED', 'type không hợp lệ')
    