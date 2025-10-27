from collections.abc import Callable, Iterator

import pytest

from fastapi.testclient import TestClient

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.main import app
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.db.user import User
from helpdesk_app_backend.models.enum.user import AccountType


# 【Fixture】TestClient を提供
# fixture：テストで毎回使う準備を自動でしてくれる仕組み
# FastAPIアプリのエンドポイントをテストコードから呼び出すためのクライアント
@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


# 【Fixture】validate_access_token を差し替え（任意の AccountType を返す）
@pytest.fixture
def override_validate_access_token() -> (
    Iterator[Callable[[AccountType], None]]
):  # 関数の型を表す型ヒント。Callable[[引数の型, ...], 返り値の型] → 引数に AccountType を1つ受け取り、値を返さない(None)関数という意味
    def _fake_validate_access_token(account_type: AccountType) -> None:
        app.dependency_overrides[validate_access_token] = lambda: account_type

    yield _fake_validate_access_token

    app.dependency_overrides.pop(validate_access_token, None)


# 【FakeSession】commit が成功する擬似セッション
# そのテストで必要なメソッドが入っていれば十分なため、使わないメソッドがあっても、問題はない。
class FakeSessionCommitSuccess:
    def __init__(  # __init__：コンストラクタ(オブジェクトを作るときに最初の設定をする場所)
        self,
    ) -> None:
        self.commit_called = False

    # 追加されたレコードへIDを付けるフリをするメソッド
    # 本来DBに保存するときに呼ぶsession.add(...)の代役
    # 追加されたインスタンスにIDを設定(今回はID=1)する(本来はDBが自動で設定する)
    def add(self, instance: User) -> None:
        instance.id = 1

    def commit(self) -> None:
        self.commit_called = True

    def rollback(self) -> None:  # テストでは何もしない空実装
        pass


# 【Fixture】FakeSessionCommitSuccess を提供（commit 成功）
@pytest.fixture
def success_session() -> FakeSessionCommitSuccess:
    return FakeSessionCommitSuccess()


# 【Fixture】get_db を差し替え（本番DBは使わない/成功版）
@pytest.fixture
def override_get_db_success(
    success_session: FakeSessionCommitSuccess,
) -> Iterator[FakeSessionCommitSuccess]:
    # 本来 get_db が返すはずのDBセッションの代わりに、適当なオブジェクトを返す関数を作成
    def _fake_db() -> Iterator[FakeSessionCommitSuccess]:
        yield success_session

    # 本物の get_db を _fake_db に差し替え（実際のDBは使わない）
    app.dependency_overrides[get_db] = _fake_db

    # このフィクスチャを使ったテスト本体が実行される
    yield success_session

    # 元の状態に戻す（差し替え解除）
    app.dependency_overrides.pop(get_db, None)


# 【FakeSession】commit で例外を投げる擬似セッション
class FakeSessionCommitError:
    def __init__(
        self,
    ) -> None:
        self.commit_called = False  # commitが呼ばれたかどうかのフラグ → 呼ばれていない
        self.rolled_back = False  # rollbackが呼ばれたかどうかのフラグ → 呼ばれていない

    def add(self, instance: User) -> None:
        instance.id = 1

    def commit(self) -> None:
        self.commit_called = True  # commitが呼ばれたことを記録
        # わざと例外を発生させる。これによりrollbackが呼ばれるようになる
        raise Exception("コミットに失敗しました")

    def rollback(self) -> None:
        self.rolled_back = True  # rollbackが呼ばれたことを記録


# 【Fixture】FakeSessionCommitError を提供（commit で例外）
@pytest.fixture
def error_session() -> FakeSessionCommitError:
    return FakeSessionCommitError()


# 【Fixture】get_db を差し替え（本番DBは使わない/失敗版）
@pytest.fixture
def override_get_db_error(
    error_session: FakeSessionCommitError,
) -> Iterator[FakeSessionCommitError]:
    # 本来 get_db が返すはずのDBセッションの代わりに、適当なオブジェクトを返す関数を作成
    def _fake_db() -> Iterator[FakeSessionCommitError]:
        yield error_session

    # 本物の get_db を _fake_db に差し替え（実際のDBは使わない）
    app.dependency_overrides[get_db] = _fake_db

    # このフィクスチャを使ったテスト本体が実行される
    yield error_session

    # 元の状態に戻す（差し替え解除）
    app.dependency_overrides.pop(get_db, None)
