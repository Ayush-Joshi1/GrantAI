from fastapi import APIRouter

from src.api.v1.routes.chat import router as chat_router
from src.api.v1.routes.deadline import router as deadline_router
from src.api.v1.routes.eligibility import router as eligibility_router
from src.api.v1.routes.history import router as history_router
from src.api.v1.routes.notification import router as notification_router
from src.api.v1.routes.orchestrate import router as orchestrate_router
from src.api.v1.routes.workflow import router as workflow_router
from src.api.v1.routes.health import router as health_router
from src.api.v1.routes.profile import router as profile_router
from src.api.v1.routes.proposal import router as proposal_router
from src.api.v1.routes.recommend import router as recommend_router
from src.api.v1.routes.search import router as search_router

api_v1_router = APIRouter()

api_v1_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_v1_router.include_router(recommend_router, prefix="/recommend", tags=["recommendations"])
api_v1_router.include_router(proposal_router, prefix="/proposal", tags=["proposal"])
api_v1_router.include_router(profile_router, prefix="/profile", tags=["profile"])
api_v1_router.include_router(history_router, prefix="/history", tags=["history"])
api_v1_router.include_router(eligibility_router, prefix="/eligibility", tags=["eligibility"])
api_v1_router.include_router(deadline_router, prefix="/deadline", tags=["deadline"])
api_v1_router.include_router(notification_router, prefix="/notifications", tags=["notifications"])
api_v1_router.include_router(orchestrate_router, prefix="/orchestrate", tags=["orchestrate"])
api_v1_router.include_router(search_router, prefix="/search", tags=["search"])
api_v1_router.include_router(workflow_router, prefix="/workflows", tags=["workflows"])
api_v1_router.include_router(health_router, prefix="", tags=["health"])

