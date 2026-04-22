from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.agendas import router as agendas_router
from routes.auth import auth_backend, current_active_user, fastapi_users
from routes.axes import router as axes_router
from routes.beliefs import router as beliefs_router
from routes.credos import router as credos_router
from routes.entities import router as entities_router
from routes.geographies import router as geographies_router
from routes.issues import router as issues_router
from routes.metrics import router as metrics_router
from models.user import User
from schemas.user import UserCreate, UserRead, UserUpdate

app = FastAPI(title="Credo API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/v1/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/v1/users",
    tags=["users"],
)

# Domain routes
app.include_router(geographies_router)
app.include_router(metrics_router)
app.include_router(agendas_router)
app.include_router(credos_router)
app.include_router(beliefs_router)
app.include_router(issues_router)
app.include_router(axes_router)
app.include_router(entities_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/v1/auth/me")
async def me(user: User = Depends(current_active_user)) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.profile.username if user.profile else None,
        "display_name": user.profile.display_name if user.profile else None,
        "created_at": str(user.created_at),
    }
