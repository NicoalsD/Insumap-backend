from fastapi import APIRouter

from app.api.v1 import assistant, auth, body_map, doctor, history, injections, reminders

api_router = APIRouter(prefix="/api/v1")
for module in (auth, body_map, injections, history, reminders, doctor, assistant):
    api_router.include_router(module.router)
