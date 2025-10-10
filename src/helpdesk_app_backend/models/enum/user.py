from enum import Enum


class AccountType(Enum):
    STAFF = "staff"  # 社員
    SUPPORTER = "supporter"  # サポーター
    ADMIN = "admin"  # 管理者
