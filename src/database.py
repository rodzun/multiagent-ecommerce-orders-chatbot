import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, func, select
import json
from sqlalchemy.orm import declarative_base, sessionmaker
import sqlite3

from models import OrderModel

Base = declarative_base()
engine = create_engine(f"sqlite:///{os.getenv('DATABASE_PATH', './db/orders.db')}")
Session = sessionmaker(bind=engine)

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    customer_name = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())

def init_db():
    Base.metadata.create_all(engine)

def create_order(order_model: OrderModel) -> int:
    session = Session()
    db_order = Order(
        product_name=order_model.product_name,
        quantity=order_model.quantity,
        price=order_model.price,
        total_price=order_model.total_price,
        customer_name=order_model.customer_name
    )
    session.add(db_order)
    session.commit()
    # Refresh to get the auto-generated ID
    session.refresh(db_order)
    order_id = db_order.order_id
    session.close()
    return order_id

def get_order_by_id(order_id: int) -> dict:
    session = Session()
    order = session.query(Order).filter_by(order_id=order_id).first()
    session.close()
    if order:
        return {
            'order_id': order.order_id,
            'product_name': order.product_name,
            'quantity': order.quantity,
            'customer_name': order.customer_name,
            'price': order.price,
            'total_price': order.total_price,
            'timestamp': order.timestamp
        }
    return None

def export_orders_to_json(filepath: str = "./db/orders_export.json"):
    """
    Exporta todas las órdenes de la base de datos SQLite a un JSON bonito.
    Usa sqlite3 puro para máxima compatibilidad y simplicidad (ideal para demos).
    """
    db_path = os.getenv('DATABASE_PATH', './db/orders.db')
    
    if not os.path.exists(db_path):
        print(f"Error: No se encuentra la base de datos en {db_path}")
        print("   Asegúrate de haber corrido init_db() y creado al menos una orden.")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders ORDER BY order_id")
    rows = cursor.fetchall()

    orders_list = [dict(row) for row in rows]
    
    conn.close()

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(orders_list, f, indent=4, default=str, ensure_ascii=False)
