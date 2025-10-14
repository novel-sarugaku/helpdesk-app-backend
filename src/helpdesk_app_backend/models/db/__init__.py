# SQLAlchemyのリレーションが正常に動作するように全てのモデルをインポート
# 短い書き方で import できるようにする
from .user import User

# 外部からインポートできるようにエクスポート
__all__ = ['User']
