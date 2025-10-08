# 管理者アカウント作成用ファイル

import argparse

from helpdesk_app_backend.models.db.base import session
from helpdesk_app_backend.models.db.user import User, UserType
from helpdesk_app_backend.services.users import get_password_hash


def create_admin_cli() -> None:
    # コマンドラインの入力（引数）を決めて、それを読み取る設定
    parser = argparse.ArgumentParser()  # コマンドがどんな引数を受け取れるかを宣言する道具を作る
    parser.add_argument("--username", required=True)  # --username という必須の引数を定義
    parser.add_argument("--email", required=True)  # --email という必須の引数を定義
    parser.add_argument("--password", required=True)  # --passwor という必須の引数を定義
    parser.add_argument(
        "--type",
        choices=["staff", "supporter", "admin"],
        required=True,
    )  # --type という必須の引数を定義
    # 実際にコマンドラインから値を読み取り、args.email / args.username / args.password / args.type のように使える入れ物を返す。
    args = parser.parse_args()

    with session() as db:
        user = User(
            username=args.username,
            email=args.email,
            password=get_password_hash(args.password),
            user_type=UserType(args.type),
        )
        db.add(user)  # DB追加準備
        db.commit()  # DBへ追加
        db.refresh(user)  # 最新状態を取り直す（DBが自動で付けた値（user_id）が反映される）
        print(
            f"管理者アカウント作成完了: id={user.user_id}, email={user.email}, type={user.user_type.value}"
        )


if __name__ == "__main__":
    create_admin_cli()
