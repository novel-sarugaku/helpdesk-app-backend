import pytest

from jose import JWTError, jwt
from passlib.context import CryptContext

import helpdesk_app_backend.logic.business.security as security

test_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 正常なパスワードで例外が発生しない
def test_validate_password_success() -> None:
    # テスト用有効パスワード（8文字以上/大文字あり/数字あり）
    valid_password = "Abcdefg1"
    # 検証
    assert security.validate_password(valid_password) is None


@pytest.mark.parametrize(
    "password, expected_message",
    [
        ("abcdefghi", "パスワードには大文字を1文字以上含めてください"),
        ("ABCDEFGH", "パスワードには数字を1文字以上含めてください"),
    ],
)
# 違反パスワードで例外が発生する
def test_validate_password_error(password: str, expected_message: str) -> None:
    # この処理で ValueError が発生することを期待
    with pytest.raises(ValueError, match=expected_message):
        security.validate_password(password)


# 正常にハッシュ化される
def test_trans_password_hash() -> None:
    test_raw_pass = "P@ssw0rd12345"
    test_hashed_pass = security.trans_password_hash(test_raw_pass)

    # 検証
    assert test_hashed_pass != test_raw_pass  # 生パスワードのまま保存されていない
    assert test_pwd_context.verify(test_raw_pass, test_hashed_pass)


# パスワードが正しい
def test_verify_password_success() -> None:
    test_raw_pass = "P@ssw0rd12345"
    test_hashed_pass = test_pwd_context.hash(test_raw_pass)

    # 検証
    assert security.verify_password(
        test_raw_pass, test_hashed_pass
    )  # 生パスワードと、DBに保存されたハッシュが一致する


# パスワードが誤っている
def test_verify_password_failed() -> None:
    test_raw_pass = "P@ssw0rd12345"
    test_hashed_pass = test_pwd_context.hash(test_raw_pass)

    # 検証
    assert (
        security.verify_password("wrong_pass", test_hashed_pass) is False
    )  # 生パスワードと、DBに保存されたハッシュが一致しない


# アクセストークンを作成することができる
def test_create_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # 偽秘密鍵・偽アルゴリズム用意
    monkeypatch.setattr(security, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(security, "ALGORITHM", "HS256")

    test_payload = {"sub": "testUser@example.com"}
    test_encoded = security.create_access_token(test_payload)

    # 検証
    # 文字列で、JWT形式（3区切り）になっているか
    # isinstance(test_encoded, str)：結果が文字列かを確認
    # test_encoded.count(".") == 2：「.」 が2個あるかを確認
    assert isinstance(test_encoded, str) and test_encoded.count(".") == 2
    # JWTの中身（payload＝クレーム）だけを取り出す
    # get_unverified_claims：JWT の中身だけを取り出すための python-jose の関数
    # JWT の claims は、トークンの中身（sub,exp,iat,issなど）を表すキー/値のセット
    claims = jwt.get_unverified_claims(test_encoded)
    assert "sub" in claims
    assert claims["sub"] == "testUser@example.com"


# デコードに成功する
def test_verify_access_token_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # 偽秘密鍵・偽アルゴリズム用意
    monkeypatch.setattr(security, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(security, "ALGORITHM", "HS256")

    test_payload = {"sub": "testUser@example.com"}
    test_token = jwt.encode(test_payload, "testsecret", algorithm="HS256")
    test_decoded = security.verify_access_token(test_token)

    # 検証
    assert "sub" in test_decoded
    assert test_decoded["sub"] == "testUser@example.com"


# デコードに失敗し、JWTErrorを検知する
def test_verify_access_token_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    # 偽秘密鍵・偽アルゴリズム用意
    monkeypatch.setattr(security, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(security, "ALGORITHM", "HS256")

    # 検証
    # エラーの検知：構文 with.pytest.raises(例外クラス) で例外を検知
    with pytest.raises(JWTError):
        # 以下を実行した際に上記エラーを検知
        security.verify_access_token("wrong_token")
