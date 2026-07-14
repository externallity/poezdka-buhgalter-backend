from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, balance, operations, roles, stats, users
from app.config import settings

app = FastAPI(title="Poezdka Buhgalter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(users.router)
app.include_router(balance.router)
app.include_router(operations.router)
app.include_router(stats.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
