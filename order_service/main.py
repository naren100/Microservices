from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, Session, DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel
from typing import List
import requests
import logging

# --------------------------------
# App Setup
# --------------------------------
app = FastAPI(title="Order Service")

# --------------------------------
# Logging
# --------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------
# Root Route (Health Check)
# --------------------------------
@app.get("/")
def root():
    return {"message": "Order Service is running"}

# --------------------------------
# Database Setup
# --------------------------------
DATABASE_URL = "sqlite:///./order.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# --------------------------------
# Database Models
# --------------------------------
class OrderDB(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    total: Mapped[float] = mapped_column()
    items: Mapped[List["OrderItemDB"]] = relationship(
        "OrderItemDB", back_populates="order", cascade="all, delete-orphan"
    )

class OrderItemDB(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_name: Mapped[str] = mapped_column()
    unit_price: Mapped[float] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    subtotal: Mapped[float] = mapped_column()

    order: Mapped[OrderDB] = relationship("OrderDB", back_populates="items")

Base.metadata.create_all(bind=engine)

# --------------------------------
# Pydantic Models
# --------------------------------
class OrderItem(BaseModel):
    item_id: int
    quantity: int

class OrderRequest(BaseModel):
    items: List[OrderItem]

class OrderLineItem(BaseModel):
    name: str
    unit_price: float
    quantity: int
    subtotal: float

    class Config:
        orm_mode = True

class OrderSummary(BaseModel):
    order_id: int
    items: List[OrderLineItem]
    total: float

# --------------------------------
# Dependency
# --------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------
# External Menu Service URL
# --------------------------------
MENU_SERVICE_URL = "http://localhost:8000"

# --------------------------------
# Order Endpoint
# --------------------------------
@app.post("/order", response_model=OrderSummary, status_code=status.HTTP_201_CREATED)
def place_order(order: OrderRequest, db: Session = Depends(get_db)):
    total = 0.0
    item_records: List[OrderItemDB] = []

    for item in order.items:
        try:
            response = requests.get(f"{MENU_SERVICE_URL}/menu/{item.item_id}")
            response.raise_for_status()
        except requests.RequestException:
            raise HTTPException(status_code=404, detail=f"Item {item.item_id} not found")

        item_data = response.json()
        subtotal = item.quantity * item_data["price"]
        total += subtotal

        item_records.append(OrderItemDB(
            item_name=item_data["name"],
            unit_price=item_data["price"],
            quantity=item.quantity,
            subtotal=subtotal
        ))

    db_order: OrderDB = OrderDB(total=round(total, 2), items=item_records)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    summary = OrderSummary(
        order_id=db_order.id,
        total=db_order.total,
        items=[
            OrderLineItem(
                name=item.item_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                subtotal=item.subtotal
            ) for item in db_order.items
        ]
    )

    logger.info(f"Placed order ID: {db_order.id} for ${db_order.total}")
    return summary

