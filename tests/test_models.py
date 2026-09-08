import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from models import OrderModel, ProductModel


def test_order_model_raises_keyerror_instead_of_validationerror_on_zero_quantity():
    with pytest.raises(KeyError):
        OrderModel(
            product_name="Laptop",
            quantity=0,
            customer_name="Ada Lovelace",
            price=250.0,
            total_price=0.0,
        )


def test_order_model_raises_keyerror_instead_of_validationerror_on_negative_price():
    with pytest.raises(KeyError):
        OrderModel(
            product_name="Laptop",
            quantity=2,
            customer_name="Ada Lovelace",
            price=-250.0,
            total_price=0.0,
        )


def test_order_model_overwrites_provided_total_price_with_price_times_quantity():
    order = OrderModel(
        product_name="Laptop",
        quantity=3,
        customer_name="Ada Lovelace",
        price=250.0,
        total_price=0.0,
    )

    assert order.total_price == 750.0


def test_product_model_rejects_description_shorter_than_ten_characters():
    with pytest.raises(ValidationError):
        ProductModel(
            product_id="P001",
            name="Mouse",
            description="too short",
            price=25.0,
            category="peripherals",
            stock_status="in stock",
        )
