"""
Unit tests for the Product class.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from product import Product


class TestProductSmoke:
    """Smoke tests for Product class."""

    def test_product_creation(self):
        """Test that a Product can be created."""
        product = Product(name="Milk", category="Dairy")
        assert product is not None

    def test_product_with_all_params(self):
        """Test Product creation with all parameters."""
        product = Product(
            name="Bread", category="Bakery", waiting_time=5, discount=True
        )
        assert product is not None


class TestProductProperties:
    """Test Product properties."""

    def test_name_property(self):
        """Test that name property returns correct value."""
        product = Product(name="Milk", category="Dairy")
        assert product.name == "Milk"

    def test_category_property(self):
        """Test that category property returns correct value."""
        product = Product(name="Milk", category="Dairy")
        assert product.category == "Dairy"

    def test_waiting_time_default(self):
        """Test that waiting_time defaults to 0."""
        product = Product(name="Milk", category="Dairy")
        assert product.waiting_time == 0

    def test_waiting_time_custom(self):
        """Test that custom waiting_time is stored."""
        product = Product(name="Milk", category="Dairy", waiting_time=10)
        assert product.waiting_time == 10

    def test_discount_default(self):
        """Test that discount defaults to False."""
        product = Product(name="Milk", category="Dairy")
        assert product.discount is False

    def test_discount_true(self):
        """Test that discount can be set to True."""
        product = Product(name="Milk", category="Dairy", discount=True)
        assert product.discount is True


class TestProductRepr:
    """Test Product string representation."""

    def test_repr_format(self):
        """Test that __repr__ returns expected format."""
        product = Product(name="Milk", category="Dairy", waiting_time=5)
        repr_str = repr(product)
        assert "Product(" in repr_str
        assert "name=Milk" in repr_str
        assert "category=Dairy" in repr_str
        assert "waiting_time=5" in repr_str


class TestProductImmutability:
    """Test that Product properties cannot be modified directly."""

    def test_name_is_readonly(self):
        """Test that name property is read-only."""
        product = Product(name="Milk", category="Dairy")
        with pytest.raises(AttributeError):
            product.name = "Cheese"

    def test_category_is_readonly(self):
        """Test that category property is read-only."""
        product = Product(name="Milk", category="Dairy")
        with pytest.raises(AttributeError):
            product.category = "Beverages"
