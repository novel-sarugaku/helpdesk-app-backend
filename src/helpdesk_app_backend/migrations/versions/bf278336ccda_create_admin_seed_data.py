"""create admin seed data

Revision ID: bf278336ccda
Revises: 25fe270ce0ee
Create Date: 2025-10-09 04:42:18.442909

"""

import os

from collections.abc import Sequence

from alembic import op
from dotenv import load_dotenv
from logic.business.security import trans_password_hash

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now

# revision identifiers, used by Alembic.
revision: str = "bf278336ccda"
down_revision: str | Sequence[str] | None = "25fe270ce0ee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 環境変数呼び出し
# os.environ：キーが存在しないことを許容しない
load_dotenv()
admin_email = os.environ["ADMIN_EMAIL"]
admin_password = os.environ["ADMIN_PASSWORD"]


# 管理者アカウント追加
def upgrade() -> None:
    """Upgrade schema."""
    # ハッシュ化
    admin_hash_password = trans_password_hash(admin_password)

    # 現在時刻（作成/更新時間）
    current_time = get_now()

    # アカウント追加
    op.execute(f"""
        INSERT INTO users (name, email, password, account_type, created_at, updated_at)
        VALUES ('管理者', '{admin_email}', '{admin_hash_password}', 'admin', '{current_time}', '{current_time}')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f"""DELETE FROM users WHERE email = '{admin_email}'""")
