from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.routers import funds, portfolio, risk_factors
from app.routers import commentary, screening, roi
from app.routers import interpretation, ingestion
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
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(funds.router)
app.include_router(portfolio.router)
app.include_router(risk_factors.router)
app.include_router(commentary.router)
app.include_router(screening.router)
app.include_router(roi.router)
app.include_router(interpretation.router)
app.include_router(ingestion.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}
