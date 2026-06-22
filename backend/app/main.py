from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.routers import funds, portfolio, risk_factors
from app.routers import commentary, screening, roi
from app.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed(session)
    yield


app = FastAPI(title="Green Cast API", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(funds.router)
app.include_router(portfolio.router)
app.include_router(risk_factors.router)
app.include_router(commentary.router)
app.include_router(screening.router)
app.include_router(roi.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}
