# SQLAlchemyのエンジン/セッションを初期化し、get_dbを提供するDB接続設定ファイル

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from helpdesk_app_backend.core.database import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# データベース接続を一時的に開いて、
# 使い終わったらきちんと閉じるという処理を、
# ジェネレーターを使って安全に管理している関数
def get_db() -> Generator:
    db = session()
    try:
        yield db
    finally:
        db.close()
