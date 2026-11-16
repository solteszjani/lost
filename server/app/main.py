from datetime import datetime, date
from pathlib import Path
from uuid import uuid4
import os, secrets, hashlib, hmac
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Response, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Text, Date, DateTime, Integer, ForeignKey, select, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("TALALTAM_DATA_DIR", str(BASE)))
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(DATA_DIR / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'talaltam.db'}")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase): pass

class ListingRow(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40))
    location: Mapped[str] = mapped_column(String(160))
    date: Mapped[str] = mapped_column(String(32))
    contact: Mapped[str] = mapped_column(String(160))
    image_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    owner_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    show_owner_name: Mapped[bool] = mapped_column(default=True, nullable=False)

class UserRow(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(190), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SessionRow(Base):
    __tablename__ = "user_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)

class MessageRow(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ReportRow(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
# Upgrade existing MVP databases without deleting existing listings.
from sqlalchemy import inspect
with engine.begin() as conn:
    cols = {c["name"] for c in inspect(engine).get_columns("listings")}
    if "owner_user_id" not in cols:
        conn.exec_driver_sql("ALTER TABLE listings ADD COLUMN owner_user_id INTEGER")
    if "show_owner_name" not in cols:
        conn.exec_driver_sql(
            "ALTER TABLE listings ADD COLUMN show_owner_name BOOLEAN NOT NULL DEFAULT TRUE"
            if engine.dialect.name == "postgresql"
            else "ALTER TABLE listings ADD COLUMN show_owner_name BOOLEAN NOT NULL DEFAULT 1"
        )
app = FastAPI(title="Találtam API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

WEB_DIR = BASE / "static"

@app.get("/", include_in_schema=False)
def web_app():
    return FileResponse(WEB_DIR / "index.html")

def db():
    session = SessionLocal()
    try: yield session
    finally: session.close()

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000)
    return salt.hex() + "$" + digest.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 310000)
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception: return False

def current_user(request: Request, session: Session = Depends(db)):
    token = request.cookies.get("talaltam_session")
    if not token: return None
    row = session.scalar(select(SessionRow).where(SessionRow.token_hash == hashlib.sha256(token.encode()).hexdigest()))
    if not row or row.expires_at < datetime.utcnow(): return None
    return session.get(UserRow, row.user_id)

def require_user(user: UserRow | None = Depends(current_user)):
    if not user: raise HTTPException(401, "A művelethez jelentkezz be.")
    return user

def serialize(row: ListingRow):
    return {"id": row.id, "owner_user_id": row.owner_user_id, "kind": row.kind, "title": row.title, "description": row.description,
            "category": row.category, "location": row.location, "date": row.date,
            "contact": row.contact, "image_url": row.image_url, "status": row.status,
            "show_owner_name": bool(row.show_owner_name), "owner_name": (None if not row.show_owner_name else None)}

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    email: str = Field(min_length=5, max_length=190)
    password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel):
    email: str
    password: str

@app.post("/auth/register", status_code=201)
def register(payload: RegisterIn, response: Response, session: Session = Depends(db)):
    email = payload.email.strip().lower()
    if session.scalar(select(UserRow).where(UserRow.email == email)):
        raise HTTPException(409, "Ezzel az e-mail-címmel már regisztráltak.")
    user = UserRow(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password))
    session.add(user); session.commit(); session.refresh(user)
    issue_session(user, response, session)
    return {"id": user.id, "name": user.name, "email": user.email}

def issue_session(user, response, session):
    token = secrets.token_urlsafe(40)
    session.add(SessionRow(token_hash=hashlib.sha256(token.encode()).hexdigest(), user_id=user.id, expires_at=datetime.utcnow()+timedelta(days=30)))
    session.commit()
    response.set_cookie("talaltam_session", token, httponly=True, samesite="lax", secure=os.getenv("VERCEL", "").lower() == "1" or os.getenv("COOKIE_SECURE", "").lower() == "true", max_age=30*24*3600, path="/")

@app.post("/auth/login")
def login(payload: LoginIn, response: Response, session: Session = Depends(db)):
    user = session.scalar(select(UserRow).where(UserRow.email == payload.email.strip().lower()))
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(401, "Hibás e-mail-cím vagy jelszó.")
    issue_session(user, response, session)
    return {"id": user.id, "name": user.name, "email": user.email}

@app.post("/auth/logout")
def logout(request: Request, response: Response, session: Session = Depends(db)):
    token=request.cookies.get("talaltam_session")
    if token:
        row=session.scalar(select(SessionRow).where(SessionRow.token_hash==hashlib.sha256(token.encode()).hexdigest()))
        if row: session.delete(row); session.commit()
    response.delete_cookie("talaltam_session", path="/")
    return {"ok": True}

@app.get("/auth/me")
def me(user: UserRow | None = Depends(current_user)):
    return {"user": ({"id":user.id,"name":user.name,"email":user.email} if user else None)}

@app.get("/health")
def health(): return {"status": "ok", "app": "Találtam"}

@app.get("/listings")
def list_listings(kind: str | None = None, category: str | None = None, q: str | None = None, session: Session = Depends(db)):
    stmt = select(ListingRow).where(ListingRow.status == "active").order_by(ListingRow.created_at.desc())
    if kind: stmt = stmt.where(ListingRow.kind == kind)
    if category: stmt = stmt.where(ListingRow.category == category)
    rows = session.scalars(stmt).all()
    if q:
        term = q.casefold()
        rows = [r for r in rows if term in r.title.casefold() or term in r.description.casefold() or term in r.location.casefold()]
    return [{**serialize(r), "owner_name": (session.get(UserRow, r.owner_user_id).name if r.show_owner_name and r.owner_user_id and session.get(UserRow, r.owner_user_id) else ("Névtelen" if not r.show_owner_name else "Ismeretlen"))} for r in rows]

@app.post("/listings", status_code=201)
async def create_listing(
    kind: str = Form(...), title: str = Form(...), description: str = Form(...),
    category: str = Form(...), location: str = Form(...), date_text: str = Form(..., alias="date"),
    contact: str = Form(...), show_owner_name: bool = Form(True), image: UploadFile | None = File(default=None), session: Session = Depends(db), user: UserRow = Depends(require_user)
):
    if kind not in ("Elveszett", "Talált"): raise HTTPException(400, "Érvénytelen bejelentéstípus.")
    if len(title.strip()) < 3 or len(description.strip()) < 10: raise HTTPException(400, "Túl rövid cím vagy leírás.")
    image_url = None
    if image:
        raw = await image.read()
        if len(raw) > 8 * 1024 * 1024: raise HTTPException(413, "A kép maximum 8 MB lehet.")
        if not raw.startswith(b"\x89PNG\r\n\x1a\n") and not raw.startswith(b"\xff\xd8\xff") and not (raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"):
            raise HTTPException(415, "Csak PNG, JPG vagy WEBP kép tölthető fel.")
        ext = "png" if raw.startswith(b"\x89PNG\r\n\x1a\n") else ("jpg" if raw.startswith(b"\xff\xd8\xff") else "webp")
        name = f"{uuid4().hex}.{ext}"
        (UPLOAD_DIR / name).write_bytes(raw)
        image_url = f"/uploads/{name}"
    row = ListingRow(kind=kind, title=title.strip(), description=description.strip(), category=category,
                     location=location.strip(), date=date_text.strip(), contact=contact.strip(), image_url=image_url, owner_user_id=user.id, show_owner_name=show_owner_name)
    session.add(row); session.commit(); session.refresh(row)
    return serialize(row)

@app.put("/listings/{listing_id}")
async def update_listing(listing_id: int, kind: str = Form(...), title: str = Form(...), description: str = Form(...), category: str = Form(...), location: str = Form(...), date_text: str = Form(..., alias="date"), contact: str = Form(...), show_owner_name: bool = Form(True), image: UploadFile | None = File(default=None), session: Session = Depends(db), user: UserRow = Depends(require_user)):
    row=session.get(ListingRow, listing_id)
    if not row: raise HTTPException(404,"A hirdetés nem található.")
    if row.owner_user_id != user.id: raise HTTPException(403,"Csak a saját hirdetésedet módosíthatod.")
    if kind not in ("Elveszett","Talált") or len(title.strip())<3 or len(description.strip())<10: raise HTTPException(400,"Ellenőrizd a megadott adatokat.")
    row.kind=kind; row.title=title.strip(); row.description=description.strip(); row.category=category; row.location=location.strip(); row.date=date_text.strip(); row.contact=contact.strip(); row.show_owner_name=show_owner_name
    if image:
        raw=await image.read()
        if len(raw)>8*1024*1024: raise HTTPException(413,"A kép maximum 8 MB lehet.")
        if not raw.startswith(b"\x89PNG\r\n\x1a\n") and not raw.startswith(b"\xff\xd8\xff") and not (raw[:4]==b"RIFF" and raw[8:12]==b"WEBP"): raise HTTPException(415,"Csak PNG, JPG vagy WEBP kép tölthető fel.")
        ext="png" if raw.startswith(b"\x89PNG\r\n\x1a\n") else ("jpg" if raw.startswith(b"\xff\xd8\xff") else "webp")
        name=f"{uuid4().hex}.{ext}"; (UPLOAD_DIR/name).write_bytes(raw); row.image_url=f"/uploads/{name}"
    session.commit(); session.refresh(row); return serialize(row)

@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, session: Session=Depends(db), user: UserRow=Depends(require_user)):
    row=session.get(ListingRow,listing_id)
    if not row: raise HTTPException(404,"A hirdetés nem található.")
    if row.owner_user_id != user.id: raise HTTPException(403,"Csak a saját hirdetésedet törölheted.")
    row.status="deleted"; session.commit(); return {"ok":True}

@app.get("/messages/{listing_id}")
def get_messages(listing_id:int, with_user:int | None = None, session:Session=Depends(db), user:UserRow=Depends(require_user)):
    listing=session.get(ListingRow,listing_id)
    if not listing or not listing.owner_user_id: raise HTTPException(404,"A hirdetés nem található.")
    if user.id != listing.owner_user_id and with_user not in (None, listing.owner_user_id):
        raise HTTPException(403,"Ehhez a beszélgetéshez nincs hozzáférésed.")
    other_id = with_user if user.id == listing.owner_user_id else listing.owner_user_id
    stmt=select(MessageRow).where(MessageRow.listing_id==listing_id,or_(
        (MessageRow.sender_id==user.id)&(MessageRow.receiver_id==other_id),
        (MessageRow.sender_id==other_id)&(MessageRow.receiver_id==user.id)
    )).order_by(MessageRow.created_at)
    rows=session.scalars(stmt).all()
    return [{"id":m.id,"sender_id":m.sender_id,"receiver_id":m.receiver_id,"body":m.body,"created_at":m.created_at.isoformat(),"mine":m.sender_id==user.id} for m in rows]

class MessageIn(BaseModel):
    body: str=Field(min_length=1,max_length=4000)
    recipient_id: int | None = None

@app.post("/messages/{listing_id}",status_code=201)
def send_message(listing_id:int,payload:MessageIn,session:Session=Depends(db),user:UserRow=Depends(require_user)):
    listing=session.get(ListingRow,listing_id)
    if not listing or not listing.owner_user_id: raise HTTPException(404,"A hirdetés nem található.")
    if user.id == listing.owner_user_id:
        if not payload.recipient_id: raise HTTPException(400,"Válaszd ki a beszélgetőpartnert.")
        recipient_id=payload.recipient_id
        exists=session.scalar(select(MessageRow).where(MessageRow.listing_id==listing_id,or_(
            (MessageRow.sender_id==user.id)&(MessageRow.receiver_id==recipient_id),
            (MessageRow.sender_id==recipient_id)&(MessageRow.receiver_id==user.id))))
        if not exists: raise HTTPException(403,"Nincs ilyen beszélgetés.")
    else:
        recipient_id=listing.owner_user_id
        if payload.recipient_id not in (None, recipient_id): raise HTTPException(403,"Érvénytelen címzett.")
    row=MessageRow(listing_id=listing_id,sender_id=user.id,receiver_id=recipient_id,body=payload.body.strip())
    session.add(row); session.commit(); session.refresh(row)
    return {"id":row.id,"sender_id":row.sender_id,"receiver_id":row.receiver_id,"body":row.body,"created_at":row.created_at.isoformat(),"mine":True}

@app.get("/inbox")
def inbox(session:Session=Depends(db),user:UserRow=Depends(require_user)):
    rows=session.scalars(select(MessageRow).where(or_(MessageRow.sender_id==user.id,MessageRow.receiver_id==user.id)).order_by(MessageRow.created_at.desc())).all()
    seen=set(); out=[]
    for m in rows:
        other_id=m.receiver_id if m.sender_id==user.id else m.sender_id
        key=(m.listing_id,other_id)
        if key in seen: continue
        seen.add(key); listing=session.get(ListingRow,m.listing_id); other=session.get(UserRow,other_id)
        out.append({"listing_id":m.listing_id,"listing_title":listing.title if listing else "Törölt hirdetés","other_user_id":other_id,"other_name":other.name if other else "Felhasználó","last_message":m.body,"created_at":m.created_at.isoformat()})
    return out

class ReportIn(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)

@app.post("/listings/{listing_id}/report", status_code=201)
def report_listing(listing_id: int, payload: ReportIn, session: Session = Depends(db)):
    row = session.get(ListingRow, listing_id)
    if not row: raise HTTPException(404, "A bejelentés nem található.")
    report = ReportRow(listing_id=listing_id, reason=payload.reason)
    session.add(report); session.commit()
    return {"status": "received"}

