from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from . import crud, models, schemas
from .database import SessionLocal, engine
from .security import create_access_token, hash_password, verify_token
from .email_utils import send_verification_email
from datetime import timedelta
import redis.asyncio as aioredis
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

models.Base.metadata.create_all(bind=engine)

load_dotenv()
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost:3000",     
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],     
)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    redis = await aioredis.from_url(os.getenv("REDIS_URL"))
    await FastAPILimiter.init(redis)

@app.on_event("shutdown")
async def shutdown_event():
    await FastAPILimiter.close()

@app.post("/contacts/", response_model=schemas.ContactInDB)
async def create_contact(
    contact: schemas.ContactCreate, 
    db: Session = Depends(get_db),
    rate_limiter: RateLimiter = Depends(RateLimiter(times=5, seconds=60))
):
    return crud.create_contact(db, contact)

@app.get("/contacts/", response_model=list[schemas.ContactInDB])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_contacts(db, skip=skip, limit=limit)

@app.get("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    return crud.update_contact(db, contact_id, contact)

@app.delete("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    return crud.delete_contact(db, contact_id)

@app.get("/contacts/search/", response_model=list[schemas.ContactInDB])
def search_contacts(query: str, db: Session = Depends(get_db)):
    return crud.search_contacts(db, query)

@app.get("/contacts/birthdays/", response_model=list[schemas.ContactInDB])
def upcoming_birthdays(db: Session = Depends(get_db)):
    return crud.get_upcoming_birthdays(db)

@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    hashed_password = hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, is_verified=False) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(hours=24))
    send_verification_email(user.email, verification_token)

    return schemas.UserResponse(id=new_user.id, email=new_user.email)

@app.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_token(token, db)

    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        user.is_verified = True 
        db.commit()
        return {"message": "Email verified successfully", "email": email}
    
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users/{user_id}/avatar/")
async def update_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        upload_result = cloudinary.uploader.upload(file.file, folder="avatars")
        avatar_url = upload_result.get("secure_url")
        
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.avatar_url = avatar_url 
        db.commit()
        return JSONResponse(content={"url": avatar_url}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
