from collections.abc import Callable, Iterator

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import ColumnProperty

from helpdesk_app_backend.core.check_token import validate_access_token
from helpdesk_app_backend.main import app
from helpdesk_app_backend.models.db.base import get_db
from helpdesk_app_backend.models.enum.user import AccountType


# 【Fixture】TestClient を提供
# fixture：テストで毎回使う準備を自動でしてくれる仕組み
# FastAPIアプリのエンドポイントをテストコードから呼び出すためのクライアント
@pytest.fixture
def test_client() -> TestClient:
    # raise_server_exceptions
    #   True（デフォルト）
    #     エラー発生 → そのまま例外を投げる
    #     test_client.post(...) の行でテストが止まる（その下の assert に進めない）
    #     検証方法：with pytest.raises(...) で例外としてチェック
    #   False
    #     エラー発生 → 例外ハンドラが動いて HTTP 500 などのレスポンスに変換
    #     test_client.post(...) は普通に戻ってくる（中身は 500）
    #     検証方法：response.status_code == 500、response.json() などレスポンスとしてチェック
    return TestClient(app, raise_server_exceptions=False)


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

    # 追加されたレコードへID、defaultが設定されているカラムにその値を付けるフリをするメソッド
    # 本来DBに保存するときに呼ぶsession.add(...)の代役
    # 追加されたインスタンスにIDを設定(今回はID=1)する(本来はDBが自動で設定する)
    def add(self, model) -> None:  # noqa: ANN001
        # model.__mapper__.iterate_properties → .__mapper__.iterate_properties は sqlAlchemy か python の modelのプロパティ
        for prop in model.__mapper__.iterate_properties:
            # isinstance（） → python の書き方 第一引数が第二引数のクラスのインスタンスかどうか
            if isinstance(prop, ColumnProperty):
                # col → id や name などカラムの情報
                # col.name → カラム名
                for col in prop.columns:
                    if col.name == "created_at" or col.name == "updated_at":
                        continue
                    if col.name == "id":
                        value = 1
                        # 第一引数のクラスに対して、第二引数の文字列をキーにして第三引数の値を返却するようにプロパティを作成
                        # 例：model.id とした場合 1 が返ってくる
                        setattr(model, col.name, value)
                    # addメソッドが呼ばれた際に、default設定されているが値が未入力の場合
                    if col.default is not None and getattr(model, col.name) is None:
                        # col.default.arg → default値 をそのまま取得してくる
                        # python 三項演算子 ifの場合 左側 そうでない場合 右側（メリット：一行でかける）
                        value = col.default.arg() if callable(col.default.arg) else col.default.arg
                        setattr(model, col.name, value)

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

    def add(self, _) -> None:  # noqa: ANN001
        return

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
