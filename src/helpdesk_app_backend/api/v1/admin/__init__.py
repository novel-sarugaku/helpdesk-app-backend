from fastapi import APIRouter

from helpdesk_app_backend.api.v1.admin.account import router as account_router

router = APIRouter()

router.include_router(account_router, prefix="/account", tags=["Account"])
