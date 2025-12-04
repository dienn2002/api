

#________SQLAlchemy__ 


from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import constants.constant as const
# Cấu hình DB


# URL kết nối: mysql+pymysql://user:password@host:port/dbname
DATABASE_URL = f"mysql+pymysql://{const.DB_USER}:{const.DB_PASSWORD}@{const.DB_HOST}:{const.DB_PORT}/{const.DB_NAME}"

# Tạo engine với pool_size tương tự
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # số kết nối giữ sẵn
    max_overflow=5,      # số kết nối tối đa ngoài pool
    pool_pre_ping=True,  # kiểm tra kết nối trước khi dùng
    echo=False           # True nếu muốn in log SQL
)

# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def session_scope():
    """
    Provide a transactional scope for database operations outside FastAPI.
    Automatically commits on success and rolls back on failure.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


print("Kết nối MySQL với SQLAlchemy thành công!")
