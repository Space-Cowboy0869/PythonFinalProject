from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base, db_session

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'employee', name='user_roles'), default='employee')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship('Transaction', back_populates='employee')
    stock_changes = relationship('StockChange', back_populates='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    
    # Relationships
    products = relationship('Product', back_populates='category')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(100))
    category_id = Column(Integer, ForeignKey('categories.id'))
    price = Column(Numeric(10, 2), nullable=False, default=0.00)
    cost_price = Column(Numeric(10, 2), nullable=False, default=0.00)
    stock = Column(Integer, nullable=False, default=0)
    is_service = Column(Boolean, default=False)
    image_filename = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship('Category', back_populates='products')
    transaction_items = relationship('TransactionItem', back_populates='product')
    stock_changes = relationship('StockChange', back_populates='product')
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('users.id'))
    total = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(Enum('cash', 'card', 'check', name='payment_methods'), default='cash')
    cash_received = Column(Numeric(12, 2), nullable=True)
    change_amount = Column(Numeric(12, 2), nullable=True)
    gcash_ref = Column(String(255), nullable=True)
    customer_name = Column(String(255))
    customer_phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship('TransactionItem', back_populates='transaction')
    employee = relationship('User', back_populates='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.id}>'

class TransactionItem(Base):
    __tablename__ = 'transaction_items'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    qty = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Relationships
    transaction = relationship('Transaction', back_populates='items')
    product = relationship('Product', back_populates='transaction_items')
    
    def __repr__(self):
        return f'<TransactionItem {self.id}>'

class StockChange(Base):
    __tablename__ = 'stock_changes'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    qty_change = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2))
    note = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship('Product', back_populates='stock_changes')
    user = relationship('User', back_populates='stock_changes')
    
    def __repr__(self):
        return f'<StockChange {self.id}>'
