from fastapi import HTTPException


# Exceptionの中のUnprocessableEntityExceptionというエラー
# Exception > HTTPException > UnprocessableEntityException
# HTTPExceptionを使う際は、status_code=やdetail=messageを記載するのがお決まり
class UnprocessableEntityException(HTTPException):
    # self：クラス自身（＝UnprocessableEntityException）記載するのがお決まり
    def __init__(self, message: str = "入力値エラー") -> None:
        # super：親クラス（＝HTTPException）
        super().__init__(status_code=422, detail=message)
