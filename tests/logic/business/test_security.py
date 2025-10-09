from datetime import timedelta

import pytest

from jose import jwt

import helpdesk_app_backend.logic.business.security as security

from helpdesk_app_backend.logic.calculate.calculate_datetime import get_now_UTC


def test_get_password_hash() -> None:
    test_raw_pass = "P@ssw0rd12345"
    test_hashed_pass = security.get_password_hash(test_raw_pass)

    # 検証
    assert test_hashed_pass != test_raw_pass  # 生パスワードのまま保存されていない
    assert (
        security.verify_password(test_raw_pass, test_hashed_pass) is True
    )  # 生パスワードと、DBに保存されたハッシュが一致する


def test_verify_password_wrong() -> None:
    test_raw_pass = "P@ssw0rd12345"
    test_hashed_pass = security.get_password_hash(test_raw_pass)
    # 検証
    assert (
        security.verify_password("wrong_pass", test_hashed_pass) is False
    )  # 生パスワードと、DBに保存されたハッシュが一致しない


def test_create_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # 偽秘密鍵・偽アルゴリズム用意
    monkeypatch.setattr(security, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(security, "ALGORITHM", "HS256")

    # JWT の exp は NumericDate（UNIX秒）なので、 UTC の datetime から timestamp()で秒にし、int()で整数化する
    tets_exp = int((get_now_UTC() + timedelta(minutes=30)).timestamp())
    test_payload = {"sub": "testUser@example.com", "exp": tets_exp}
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
    assert claims["sub"] == "testUser@example.com"
    assert claims["exp"] == tets_exp


def test_verify_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # 偽秘密鍵・偽アルゴリズム用意
    monkeypatch.setattr(security, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(security, "ALGORITHM", "HS256")

    # JWT の exp は NumericDate（UNIX秒）なので、 UTC の datetime から timestamp()で秒にし、int()で整数化する
    tets_exp = int((get_now_UTC() + timedelta(minutes=30)).timestamp())
    test_payload = {"sub": "testUser@example.com", "exp": tets_exp}
    test_token = jwt.encode(test_payload, "testsecret", algorithm="HS256")
    test_decoded = security.verify_access_token(test_token)

    # 検証
    assert test_decoded["sub"] == "testUser@example.com"
    assert test_decoded["exp"] == tets_exp
