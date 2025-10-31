from fastapi import APIRouter

from helpdesk_app_backend.api.v1.admin import router as admin_router
from helpdesk_app_backend.api.v1.auth import router as auth_router
from helpdesk_app_backend.api.v1.healthcheck import router as healthcheck_router
from helpdesk_app_backend.api.v1.ticket import router as ticket_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])
router.include_router(admin_router, prefix="/admin")
router.include_router(ticket_router, prefix="/ticket", tags=["Ticket"])
