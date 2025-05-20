from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from pydantic import BaseModel
from typing import List
import logging

# --------------------------------
# App & Logging Setup
# --------------------------------
app = FastAPI(title="Menu Service")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------
# Root Endpoint
# --------------------------------
@app.get("/")
def root():
    return {"message": "Menu Service is running"}

# --------------------------------
# Database Setup
# --------------------------------
DATABASE_URL = "sqlite:///./menu.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class MenuItemDB(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)

Base.metadata.create_all(bind=engine)

# --------------------------------
# Pydantic Models
# --------------------------------
class MenuItem(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        orm_mode = True

# --------------------------------
# Dependency Injection
# --------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------
# Endpoints
# --------------------------------
@app.post("/menu/add", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
def add_item(item: MenuItem, db: Session = Depends(get_db)):
    existing = db.query(MenuItemDB).filter_by(id=item.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists.")

    db_item = MenuItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    logger.info(f"Added item: {db_item.name}")
    return db_item

@app.get("/menu", response_model=List[MenuItem])
def get_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItemDB).all()
    return items

@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItemDB).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item



