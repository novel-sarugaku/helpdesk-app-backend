from pydantic import BaseModel


# チケット追加（POST）
class CreateTicketRequest(BaseModel):
    title: str
    is_public: bool
    description: str
