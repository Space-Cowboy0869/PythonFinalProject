from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'pos_db')

# Create database engine
DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URI, pool_recycle=3600)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def ensure_schema():
    insp = inspect(engine)

    with engine.begin() as conn:
        if insp.has_table('products'):
            cols = {c['name'] for c in insp.get_columns('products')}
            if 'sku' not in cols:
                conn.execute(text('ALTER TABLE products ADD COLUMN sku VARCHAR(100)'))
            if 'is_service' not in cols:
                conn.execute(text('ALTER TABLE products ADD COLUMN is_service TINYINT(1) NOT NULL DEFAULT 0'))
            if 'image_filename' not in cols:
                conn.execute(text('ALTER TABLE products ADD COLUMN image_filename VARCHAR(255)'))
            if 'created_at' not in cols:
                conn.execute(text('ALTER TABLE products ADD COLUMN created_at DATETIME'))
            if 'cost_price' not in cols:
                conn.execute(text('ALTER TABLE products ADD COLUMN cost_price DECIMAL(10,2) NOT NULL DEFAULT 0.00'))

        if insp.has_table('transactions'):
            cols = {c['name'] for c in insp.get_columns('transactions')}
            if 'payment_method' not in cols:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN payment_method ENUM('cash','card','check') NOT NULL DEFAULT 'cash'"))
            if 'customer_name' not in cols:
                conn.execute(text('ALTER TABLE transactions ADD COLUMN customer_name VARCHAR(255)'))
            if 'customer_phone' not in cols:
                conn.execute(text('ALTER TABLE transactions ADD COLUMN customer_phone VARCHAR(50)'))
            if 'created_at' not in cols:
                conn.execute(text('ALTER TABLE transactions ADD COLUMN created_at DATETIME'))
            if 'cash_received' not in cols:
                conn.execute(text('ALTER TABLE transactions ADD COLUMN cash_received DECIMAL(12,2) NULL'))
            if 'change_amount' not in cols:
                conn.execute(text('ALTER TABLE transactions ADD COLUMN change_amount DECIMAL(12,2) NULL'))
            if 'gcash_ref' not in cols:
                conn.execute(text('ALTER TABLE transactions ADD COLUMN gcash_ref VARCHAR(255) NULL'))

        if insp.has_table('transaction_items'):
            cols = {c['name'] for c in insp.get_columns('transaction_items')}
            if 'cost_price' not in cols:
                conn.execute(text('ALTER TABLE transaction_items ADD COLUMN cost_price DECIMAL(10,2) NOT NULL DEFAULT 0.00'))

        if insp.has_table('stock_changes'):
            cols = {c['name'] for c in insp.get_columns('stock_changes')}
            if 'unit_cost' not in cols:
                conn.execute(text('ALTER TABLE stock_changes ADD COLUMN unit_cost DECIMAL(10,2) NULL'))

        if insp.has_table('users'):
            cols = {c['name'] for c in insp.get_columns('users')}
            if 'role' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN role ENUM('admin','employee') NOT NULL DEFAULT 'employee'"))
            if 'created_at' not in cols:
                conn.execute(text('ALTER TABLE users ADD COLUMN created_at DATETIME'))

def init_db():
    # Import all models here to ensure they are registered with SQLAlchemy
    from .models import User, Product, Category, Transaction, TransactionItem, StockChange
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

    ensure_schema()
    
    # Create admin user if not exists
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin'),
            role='admin'
        )
        db_session.add(admin)
        db_session.commit()

class BaseModel:
    """Base model class that provides common functionality."""
    
    def save(self):
        """Save the current object to the database."""
        try:
            db_session.add(self)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            print(f"Error saving to database: {e}")
            return False
    
    def delete(self):
        """Delete the current object from the database."""
        try:
            db_session.delete(self)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            print(f"Error deleting from database: {e}")
            return False
