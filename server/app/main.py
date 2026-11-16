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
from sqlalchemy import create_engine, String, Text, Date, DateTime, Integer, Float, Boolean, ForeignKey, select, or_, and_
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
    district: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class UserRow(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(190), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    successful_returns: Mapped[int] = mapped_column(Integer, default=0)
    rating_sum: Mapped[int] = mapped_column(Integer, default=0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    avatar_url: Mapped[str | None] = mapped_column(String(300), nullable=True)

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
    image_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class ReportRow(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NotificationRow(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(300), default="/")
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class BlockRow(Base):
    __tablename__ = "user_blocks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    blocker_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    blocked_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

class ArchiveRow(Base):
    __tablename__ = "conversation_archives"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    listing_id: Mapped[int] = mapped_column(Integer)
    other_user_id: Mapped[int] = mapped_column(Integer)

class RatingRow(Base):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer)
    note: Mapped[str] = mapped_column(String(500), default="")
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
with engine.begin() as conn:
    cols = {c["name"] for c in inspect(engine).get_columns("listings")}
    if "district" not in cols: conn.exec_driver_sql("ALTER TABLE listings ADD COLUMN district VARCHAR(40)")
    if "latitude" not in cols: conn.exec_driver_sql("ALTER TABLE listings ADD COLUMN latitude FLOAT")
    if "longitude" not in cols: conn.exec_driver_sql("ALTER TABLE listings ADD COLUMN longitude FLOAT")
    if "resolved_at" not in cols: conn.exec_driver_sql("ALTER TABLE listings ADD COLUMN resolved_at TIMESTAMP")
with engine.begin() as conn:
    ucols={c["name"] for c in inspect(engine).get_columns("users")}
    for name,ddl in [("phone","VARCHAR(30)"),("phone_verified","BOOLEAN NOT NULL DEFAULT FALSE" if engine.dialect.name=="postgresql" else "BOOLEAN NOT NULL DEFAULT 0"),("successful_returns","INTEGER NOT NULL DEFAULT 0"),("rating_sum","INTEGER NOT NULL DEFAULT 0"),("rating_count","INTEGER NOT NULL DEFAULT 0"),("avatar_url","VARCHAR(300)")]:
        if name not in ucols: conn.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {name} {ddl}")
    mcols={c["name"] for c in inspect(engine).get_columns("messages")}
    if "image_url" not in mcols: conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN image_url VARCHAR(300)")
    if "read_at" not in mcols: conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN read_at TIMESTAMP")
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
            "contact": None, "image_url": row.image_url, "status": row.status,
            "show_owner_name": bool(row.show_owner_name), "district": row.district, "latitude": row.latitude, "longitude": row.longitude, "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None, "owner_name": (None if not row.show_owner_name else None)}

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
    return {"user": ({"id":user.id,"name":user.name,"email":user.email,"avatar_url":user.avatar_url} if user else None)}

@app.get("/health")
def health(): return {"status": "ok", "app": "Találtam"}

@app.get("/listings")
def list_listings(kind: str | None = None, category: str | None = None, district: str | None = None, q: str | None = None, city: str | None = None, session: Session = Depends(db)):
    stmt = select(ListingRow).where(ListingRow.status == "active").order_by(ListingRow.created_at.desc())
    if kind: stmt = stmt.where(ListingRow.kind == kind)
    if category: stmt = stmt.where(ListingRow.category == category)
    if district: stmt = stmt.where(ListingRow.district == district)
    rows = session.scalars(stmt).all()
    if q:
        term = q.casefold()
        rows = [r for r in rows if term in r.title.casefold() or term in r.description.casefold() or term in r.location.casefold()]
    return [{**serialize(r), "owner_name": (session.get(UserRow, r.owner_user_id).name if r.show_owner_name and r.owner_user_id and session.get(UserRow, r.owner_user_id) else ("Névtelen" if not r.show_owner_name else "Ismeretlen"))} for r in rows]

@app.get("/listings/{listing_id}")
def get_listing(listing_id: int, session: Session = Depends(db)):
    row = session.get(ListingRow, listing_id)
    if not row or row.status != "active":
        raise HTTPException(404, "A hirdetés nem található vagy már lezárták.")
    owner = session.get(UserRow, row.owner_user_id) if row.owner_user_id else None
    return {**serialize(row), "owner_name": (owner.name if row.show_owner_name and owner else ("Névtelen" if not row.show_owner_name else "Ismeretlen"))}

@app.post("/listings", status_code=201)
async def create_listing(
    kind: str = Form(...), title: str = Form(...), description: str = Form(...),
    category: str = Form(...), location: str = Form(...), date_text: str = Form(..., alias="date"),
    contact: str = Form(...), show_owner_name: bool = Form(True), district: str = Form(...), latitude: float | None = Form(None), longitude: float | None = Form(None), image: UploadFile | None = File(default=None), session: Session = Depends(db), user: UserRow = Depends(require_user)
):
    if kind not in ("Elveszett", "Talált"): raise HTTPException(400, "Érvénytelen bejelentéstípus.")
    if district not in [f"{i}. kerület" for i in range(1,24)]: raise HTTPException(400, "Válassz budapesti kerületet.")
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
                     location=location.strip(), date=date_text.strip(), contact=contact.strip(), image_url=image_url, owner_user_id=user.id, show_owner_name=show_owner_name, district=district, latitude=latitude, longitude=longitude)
    session.add(row); session.commit(); session.refresh(row)
    notify_matches(row, session)
    return serialize(row)

@app.put("/listings/{listing_id}")
async def update_listing(listing_id: int, kind: str = Form(...), title: str = Form(...), description: str = Form(...), category: str = Form(...), location: str = Form(...), date_text: str = Form(..., alias="date"), contact: str = Form(...), show_owner_name: bool = Form(True), district: str = Form(...), latitude: float | None = Form(None), longitude: float | None = Form(None), image: UploadFile | None = File(default=None), session: Session = Depends(db), user: UserRow = Depends(require_user)):
    row=session.get(ListingRow, listing_id)
    if not row: raise HTTPException(404,"A hirdetés nem található.")
    if row.owner_user_id != user.id: raise HTTPException(403,"Csak a saját hirdetésedet módosíthatod.")
    if kind not in ("Elveszett","Talált") or len(title.strip())<3 or len(description.strip())<10: raise HTTPException(400,"Ellenőrizd a megadott adatokat.")
    row.kind=kind; row.title=title.strip(); row.description=description.strip(); row.category=category; row.location=location.strip(); row.date=date_text.strip(); row.contact=contact.strip(); row.show_owner_name=show_owner_name; row.district=district; row.latitude=latitude; row.longitude=longitude
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
    for m in rows:
        if m.receiver_id==user.id and not m.read_at: m.read_at=datetime.utcnow()
    session.commit()
    return [{"id":m.id,"sender_id":m.sender_id,"receiver_id":m.receiver_id,"body":m.body,"image_url":m.image_url,"read":bool(m.read_at),"created_at":m.created_at.isoformat(),"mine":m.sender_id==user.id} for m in rows]

class MessageIn(BaseModel):
    body: str=Field(default="",max_length=4000)
    image_url: str | None = None
    recipient_id: int | None = None

@app.post("/messages/{listing_id}",status_code=201)
def send_message(listing_id:int,payload:MessageIn,session:Session=Depends(db),user:UserRow=Depends(require_user)):
    listing=session.get(ListingRow,listing_id)
    if not listing or not listing.owner_user_id: raise HTTPException(404,"A hirdetés nem található.")
    if not payload.body.strip() and not payload.image_url: raise HTTPException(400,"Írj üzenetet vagy csatolj képet.")
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
    if session.scalar(select(BlockRow).where(or_(and_(BlockRow.blocker_id==user.id,BlockRow.blocked_id==recipient_id),and_(BlockRow.blocker_id==recipient_id,BlockRow.blocked_id==user.id)))): raise HTTPException(403,"A beszélgetés nem elérhető.")
    row=MessageRow(listing_id=listing_id,sender_id=user.id,receiver_id=recipient_id,body=payload.body.strip(),image_url=payload.image_url)
    session.add(row); session.commit(); session.refresh(row)
    notify(session,recipient_id,"Új üzenet",f"Új üzeneted érkezett: {listing.title}","/"); session.commit()
    return {"id":row.id,"sender_id":row.sender_id,"receiver_id":row.receiver_id,"body":row.body,"image_url":row.image_url,"read":False,"created_at":row.created_at.isoformat(),"mine":True}

@app.get("/inbox")
def inbox(session:Session=Depends(db),user:UserRow=Depends(require_user)):
    rows=session.scalars(select(MessageRow).where(or_(MessageRow.sender_id==user.id,MessageRow.receiver_id==user.id)).order_by(MessageRow.created_at.desc())).all()
    seen=set(); out=[]
    for m in rows:
        other_id=m.receiver_id if m.sender_id==user.id else m.sender_id
        key=(m.listing_id,other_id)
        if session.scalar(select(ArchiveRow).where(ArchiveRow.user_id==user.id,ArchiveRow.listing_id==m.listing_id,ArchiveRow.other_user_id==other_id)): continue
        if session.scalar(select(BlockRow).where(or_(and_(BlockRow.blocker_id==user.id,BlockRow.blocked_id==other_id),and_(BlockRow.blocker_id==other_id,BlockRow.blocked_id==user.id)))): continue
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



# ---- Találtam közösségi funkciók ----
def haversine(lat1,lon1,lat2,lon2):
    from math import radians,sin,cos,asin,sqrt
    dlat=radians(lat2-lat1); dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 6371*2*asin(sqrt(a))

def notify(session,user_id,title,body,url="/"):
    if user_id: session.add(NotificationRow(user_id=user_id,title=title,body=body,url=url))

def similarity(a,b):
    words=set((a.title+" "+a.description+" "+a.category).casefold().split())
    other=set((b.title+" "+b.description+" "+b.category).casefold().split())
    return len(words & other)/max(1,len(words | other))

def notify_matches(row,session):
    if not row.owner_user_id: return
    opposite="Talált" if row.kind=="Elveszett" else "Elveszett"
    candidates=session.scalars(select(ListingRow).where(ListingRow.status=="active",ListingRow.kind==opposite,ListingRow.id!=row.id)).all()
    for candidate in candidates:
        dist=None
        if row.latitude is not None and row.longitude is not None and candidate.latitude is not None and candidate.longitude is not None:
            dist=haversine(row.latitude,row.longitude,candidate.latitude,candidate.longitude)
            if dist>15: continue
        score=similarity(row,candidate)
        same_cat=row.category.casefold()==candidate.category.casefold()
        same_district=bool(row.district and row.district==candidate.district)
        if score>=0.12 or same_cat or same_district:
            for uid in {row.owner_user_id,candidate.owner_user_id}:
                if uid and uid not in (None,): notify(session,uid,"Lehetséges találat",f"Hasonló bejelentés: {row.title if uid==candidate.owner_user_id else candidate.title}"+(f" · {dist:.1f} km" if dist is not None else ""),"/")
    session.commit()

@app.get("/map/listings")
def map_listings(district:str|None=None,kind:str|None=None,lat:float|None=None,lon:float|None=None,radius:float=50,session:Session=Depends(db)):
    # A térképes nézet kizárólag Budapest közigazgatási területének közelítő határain belül jelenít meg adatokat.
    south, north, west, east = 47.34, 47.62, 18.92, 19.35
    rows=session.scalars(select(ListingRow).where(ListingRow.status=="active",ListingRow.latitude.is_not(None),ListingRow.longitude.is_not(None))).all()
    out=[]
    for r in rows:
        if not (south <= r.latitude <= north and west <= r.longitude <= east): continue
        if district and r.district!=district: continue
        if kind and r.kind!=kind: continue
        d=haversine(lat,lon,r.latitude,r.longitude) if lat is not None and lon is not None else None
        if d is not None and d>radius: continue
        out.append({**serialize(r),"distance_km":round(d,1) if d is not None else None})
    return out

@app.get("/matches/{listing_id}")
def get_matches(listing_id:int,session:Session=Depends(db)):
    row=session.get(ListingRow,listing_id)
    if not row: raise HTTPException(404,"A bejelentés nem található.")
    opposite="Talált" if row.kind=="Elveszett" else "Elveszett"
    candidates=session.scalars(select(ListingRow).where(ListingRow.status=="active",ListingRow.kind==opposite,ListingRow.id!=row.id)).all()
    scored=[]
    for c in candidates:
        score=similarity(row,c)+(0.25 if row.category==c.category else 0)+(0.2 if row.district and row.district==c.district else 0)
        dist=haversine(row.latitude,row.longitude,c.latitude,c.longitude) if None not in (row.latitude,row.longitude,c.latitude,c.longitude) else None
        if dist is not None: score+=max(0,0.25-dist/100)
        if score>=0.12: scored.append((score,c,dist))
    scored.sort(key=lambda x:x[0],reverse=True)
    return [{**serialize(c),"owner_name":(session.get(UserRow,c.owner_user_id).name if c.show_owner_name and c.owner_user_id and session.get(UserRow,c.owner_user_id) else ("Névtelen" if not c.show_owner_name else "Ismeretlen")),"match_score":min(99,round(score*100)),"distance_km":round(dist,1) if dist is not None else None} for score,c,dist in scored[:10]]

@app.get("/notifications")
def get_notifications(session:Session=Depends(db),user:UserRow=Depends(require_user)):
    rows=session.scalars(select(NotificationRow).where(NotificationRow.user_id==user.id).order_by(NotificationRow.created_at.desc()).limit(50)).all()
    return [{"id":n.id,"title":n.title,"body":n.body,"url":n.url,"read":n.read,"created_at":n.created_at.isoformat()} for n in rows]

@app.post("/notifications/read")
def read_notifications(session:Session=Depends(db),user:UserRow=Depends(require_user)):
    for n in session.scalars(select(NotificationRow).where(NotificationRow.user_id==user.id,NotificationRow.read==False)).all(): n.read=True
    session.commit(); return {"ok":True}

@app.post("/listings/{listing_id}/resolve")
def resolve_listing(listing_id:int,session:Session=Depends(db),user:UserRow=Depends(require_user)):
    row=session.get(ListingRow,listing_id)
    if not row: raise HTTPException(404,"A bejelentés nem található.")
    if row.owner_user_id!=user.id: raise HTTPException(403,"Csak a saját bejelentésedet zárhatod le.")
    if row.status!="resolved":
        row.status="resolved"; row.resolved_at=datetime.utcnow(); user.successful_returns=(user.successful_returns or 0)+1
        session.add(row); session.commit()
    return {"ok":True,"successful_returns":user.successful_returns}

@app.get("/stats")
def stats(session:Session=Depends(db)):
    total=session.scalar(select(ListingRow).where(ListingRow.status=="resolved"))
    return {"successful_returns":session.query(ListingRow).filter(ListingRow.status=="resolved").count()}

@app.get("/profile/{user_id}")
def profile(user_id:int,session:Session=Depends(db)):
    u=session.get(UserRow,user_id)
    if not u: raise HTTPException(404,"A profil nem található.")
    return {"id":u.id,"name":u.name,"avatar_url":u.avatar_url,"phone_verified":bool(u.phone_verified),"successful_returns":u.successful_returns or 0,"rating":round((u.rating_sum or 0)/(u.rating_count or 1),1) if u.rating_count else None,"rating_count":u.rating_count or 0,"member_since":u.created_at.date().isoformat()}

class PhoneIn(BaseModel): phone:str=Field(min_length=8,max_length=30)
@app.post("/profile/phone")
def save_phone(payload:PhoneIn,session:Session=Depends(db),user:UserRow=Depends(require_user)):
    # Phone is stored as unverified. Real SMS verification requires an SMS provider and credentials.
    user.phone=payload.phone.strip(); user.phone_verified=False; session.commit()
    return {"phone":user.phone,"verified":False,"message":"A telefonszám mentve. SMS-ellenőrzés csak SMS-szolgáltató csatlakoztatása után aktiválható."}

class ProfileEmailIn(BaseModel): email: str = Field(min_length=5, max_length=190)
class ProfilePasswordIn(BaseModel): current_password: str = Field(min_length=1, max_length=128); new_password: str = Field(min_length=8, max_length=128)

@app.put("/profile/email")
def change_email(payload: ProfileEmailIn, session: Session=Depends(db), user: UserRow=Depends(require_user)):
    email=payload.email.strip().lower()
    if session.scalar(select(UserRow).where(UserRow.email==email,UserRow.id!=user.id)):
        raise HTTPException(409,"Ezzel az e-mail-címmel már létezik fiók.")
    user.email=email; session.commit(); return {"ok":True,"email":email}

@app.put("/profile/password")
def change_password(payload: ProfilePasswordIn, session: Session=Depends(db), user: UserRow=Depends(require_user)):
    if not verify_password(payload.current_password,user.password_hash): raise HTTPException(400,"A jelenlegi jelszó nem megfelelő.")
    user.password_hash=hash_password(payload.new_password)
    # A jelszócsere után a többi aktív munkamenet megszűnik.
    token=None
    # Keep the current browser session; revoke all other sessions by matching request cookie below is not available here.
    session.commit(); return {"ok":True,"message":"A jelszó sikeresen módosult."}

@app.post("/profile/avatar")
async def upload_avatar(image: UploadFile=File(...), session: Session=Depends(db), user: UserRow=Depends(require_user)):
    raw=await image.read()
    if len(raw)>5*1024*1024: raise HTTPException(413,"A profilkép maximum 5 MB lehet.")
    if not (raw.startswith(b"\x89PNG\r\n\x1a\n") or raw.startswith(b"\xff\xd8\xff") or (raw[:4]==b"RIFF" and raw[8:12]==b"WEBP")): raise HTTPException(415,"Csak PNG, JPG vagy WEBP kép tölthető fel.")
    ext="png" if raw.startswith(b"\x89PNG") else ("jpg" if raw.startswith(b"\xff\xd8") else "webp")
    name=f"avatar_{user.id}_{uuid4().hex}.{ext}"; (UPLOAD_DIR/name).write_bytes(raw); user.avatar_url=f"/uploads/{name}"; session.commit()
    return {"avatar_url":user.avatar_url}

@app.delete("/profile/account")
def delete_account(session: Session=Depends(db), user: UserRow=Depends(require_user)):
    # A felhasználó személyes adatait és kapcsolódó tartalmait eltávolítjuk; a közösségi hirdetéseket töröltként jelöljük.
    for listing in session.scalars(select(ListingRow).where(ListingRow.owner_user_id==user.id)).all():
        listing.status="deleted"; listing.contact=""
    for model in (SessionRow, NotificationRow, BlockRow, ArchiveRow, RatingRow, MessageRow):
        if model is BlockRow: session.query(model).filter(or_(model.blocker_id==user.id,model.blocked_id==user.id)).delete(synchronize_session=False)
        elif model is ArchiveRow: session.query(model).filter(model.user_id==user.id).delete(synchronize_session=False)
        elif model is RatingRow: session.query(model).filter(or_(model.from_user_id==user.id,model.to_user_id==user.id)).delete(synchronize_session=False)
        elif model is MessageRow: session.query(model).filter(or_(model.sender_id==user.id,model.receiver_id==user.id)).delete(synchronize_session=False)
        else: session.query(model).filter(model.user_id==user.id).delete(synchronize_session=False)
    session.delete(user); session.commit(); return {"ok":True}

@app.post("/search/by-image")
async def search_by_image(image: UploadFile=File(...), session: Session=Depends(db)):
    raw=await image.read()
    if len(raw)>8*1024*1024: raise HTTPException(413,"A keresőkép maximum 8 MB lehet.")
    try:
        from PIL import Image, ImageOps
        import io
        def ahash(data):
            im=Image.open(io.BytesIO(data)).convert("RGB")
            im=ImageOps.fit(im,(8,8)).convert("L")
            px=list(im.getdata()); avg=sum(px)/len(px)
            return [v>=avg for v in px]
        query_hash=ahash(raw)
    except Exception:
        raise HTTPException(415,"A feltöltött fájl nem feldolgozható kép. PNG, JPG vagy WEBP használható.")
    rows=session.scalars(select(ListingRow).where(ListingRow.status=="active",ListingRow.image_url.is_not(None))).all()
    results=[]
    for row in rows:
        path=UPLOAD_DIR / Path(row.image_url).name
        if not path.exists(): continue
        try:
            candidate_hash=ahash(path.read_bytes())
            distance=sum(a!=b for a,b in zip(query_hash,candidate_hash))
            similarity_pct=round((1-distance/64)*100)
            if similarity_pct>=58:
                owner=session.get(UserRow,row.owner_user_id) if row.owner_user_id else None
                results.append({**serialize(row),"owner_name":(owner.name if row.show_owner_name and owner else ("Névtelen" if not row.show_owner_name else "Ismeretlen")),"image_similarity":similarity_pct})
        except Exception: continue
    results.sort(key=lambda x:x["image_similarity"],reverse=True)
    return {"results":results[:20],"method":"perceptual_hash","note":"A képi hasonlóság előszűrés. A hasonló szín- és fényviszonyok befolyásolhatják az eredményt."}

class RatingIn(BaseModel): listing_id:int; score:int=Field(ge=1,le=5); note:str=Field(default="",max_length=500)
@app.post("/ratings",status_code=201)
def rate_user(payload:RatingIn,session:Session=Depends(db),user:UserRow=Depends(require_user)):
    listing=session.get(ListingRow,payload.listing_id)
    if not listing or listing.status!="resolved" or not listing.owner_user_id or listing.owner_user_id==user.id: raise HTTPException(400,"Értékelés csak lezárt ügylet után adható.")
    if session.scalar(select(RatingRow).where(RatingRow.listing_id==listing.id,RatingRow.from_user_id==user.id)): raise HTTPException(409,"Ezt a teljesítést már értékelted.")
    session.add(RatingRow(listing_id=listing.id,from_user_id=user.id,to_user_id=listing.owner_user_id,score=payload.score,note=payload.note)); target=session.get(UserRow,listing.owner_user_id); target.rating_sum=(target.rating_sum or 0)+payload.score; target.rating_count=(target.rating_count or 0)+1; session.commit(); return {"ok":True}

@app.post("/conversations/{listing_id}/{other_id}/archive")
def archive_conversation(listing_id:int,other_id:int,session:Session=Depends(db),user:UserRow=Depends(require_user)):
    if not session.scalar(select(ArchiveRow).where(ArchiveRow.user_id==user.id,ArchiveRow.listing_id==listing_id,ArchiveRow.other_user_id==other_id)):
        session.add(ArchiveRow(user_id=user.id,listing_id=listing_id,other_user_id=other_id)); session.commit()
    return {"ok":True}

@app.post("/users/{other_id}/block")
def block_user(other_id:int,session:Session=Depends(db),user:UserRow=Depends(require_user)):
    if other_id==user.id: raise HTTPException(400,"Saját magadat nem tilthatod.")
    if not session.scalar(select(BlockRow).where(BlockRow.blocker_id==user.id,BlockRow.blocked_id==other_id)):
        session.add(BlockRow(blocker_id=user.id,blocked_id=other_id)); session.commit()
    return {"ok":True}

@app.post("/messages/upload",status_code=201)
async def upload_chat_image(image:UploadFile=File(...),user:UserRow=Depends(require_user)):
    raw=await image.read()
    if len(raw)>5*1024*1024: raise HTTPException(413,"A kép maximum 5 MB lehet.")
    if not (raw.startswith(b"\x89PNG\r\n\x1a\n") or raw.startswith(b"\xff\xd8\xff") or (raw[:4]==b"RIFF" and raw[8:12]==b"WEBP")): raise HTTPException(415,"Csak PNG, JPG vagy WEBP kép tölthető fel.")
    ext="png" if raw.startswith(b"\x89PNG") else ("jpg" if raw.startswith(b"\xff\xd8") else "webp")
    name=f"chat_{uuid4().hex}.{ext}"; (UPLOAD_DIR/name).write_bytes(raw); return {"image_url":f"/uploads/{name}"}
