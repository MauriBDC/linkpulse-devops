from contextlib import asynccontextmanager
from datetime import datetime, timezone
import secrets
import string

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, ConfigDict
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Link


ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


@asynccontextmanager
async def lifespan(_: FastAPI):
    # MVP only. Replace with Alembic migrations in the next project stage.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="LinkPulse API",
    version="0.1.0",
    description="URL shortener used as a production-style DevOps workload.",
    lifespan=lifespan,
)


class LinkCreate(BaseModel):
    url: HttpUrl


class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
    last_accessed_at: datetime | None


@app.get("/health/live", tags=["health"])
def liveness():
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc

    return {"status": "ready"}


@app.post("/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED, tags=["links"])
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    for _ in range(5):
        short_code = generate_short_code()
        existing = db.scalar(select(Link).where(Link.short_code == short_code))
        if existing is None:
            break
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not allocate short code",
        )

    link = Link(
        original_url=str(payload.url),
        short_code=short_code,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@app.get("/links/{short_code}/stats", response_model=LinkResponse, tags=["links"])
def link_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.short_code == short_code))
    if link is None:
        raise HTTPException(status_code=404, detail="link not found")
    return link


@app.get("/{short_code}", include_in_schema=False)
def redirect(short_code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.short_code == short_code))
    if link is None:
        raise HTTPException(status_code=404, detail="link not found")

    link.clicks += 1
    link.last_accessed_at = datetime.now(timezone.utc)
    db.commit()

    return RedirectResponse(url=link.original_url, status_code=status.HTTP_302_FOUND)
