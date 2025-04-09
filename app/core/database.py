import os
from typing import Dict, Any, Optional, List, Generator, TypeVar, Type
from contextlib import contextmanager
import time

from app.core.logging import log_info, log_error, log_warning

# Define a Session type for type hints
T = TypeVar('T')

try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session, relationship
    from sqlalchemy.pool import QueuePool
    DATABASE_AVAILABLE = True
    SessionType = Session
except ImportError:
    log_warning("SQLAlchemy not available, database integration will be disabled")
    DATABASE_AVAILABLE = False
    # Create dummy Session class for type hints when SQLAlchemy is not available
    class SessionType:
        def __init__(self):
            pass
        def close(self):
            pass
        def commit(self):
            pass
        def rollback(self):
            pass
        def execute(self, *args, **kwargs):
            return []

# Create Base class for SQLAlchemy models
Base = declarative_base() if DATABASE_AVAILABLE else object

class DatabaseClient:
    """Database client for SQL database operations."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.initialized = False

        if not DATABASE_AVAILABLE:
            log_warning("SQLAlchemy not available, database integration is disabled")
            return

        try:
            self.initialize()
        except Exception as e:
            log_error(f"Failed to initialize database: {str(e)}")

    def initialize(self):
        """Initialize database connection."""
        if self.initialized or not DATABASE_AVAILABLE:
            return

        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            log_warning("DATABASE_URL not set, using SQLite database")
            database_url = "sqlite:///./bitebase.db"

        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections after 30 minutes
            echo=False  # Set to True for SQL query logging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.initialized = True
        log_info(f"Database initialized with {database_url}")

    def create_tables(self):
        """Create all tables defined in SQLAlchemy models."""
        if not self.initialized or not DATABASE_AVAILABLE:
            log_warning("Database not initialized, cannot create tables")
            return

        try:
            Base.metadata.create_all(bind=self.engine)
            log_info("Database tables created")
        except Exception as e:
            log_error(f"Failed to create database tables: {str(e)}")
            raise

    @contextmanager
    def get_session(self) -> Generator[SessionType, None, None]:
        """Get a database session."""
        if not self.initialized or not DATABASE_AVAILABLE:
            raise Exception("Database not initialized")

        session = self.SessionLocal()
        start_time = time.time()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            log_error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
            log_info(f"Database session completed in {time.time() - start_time:.4f} seconds")

    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a raw SQL query."""
        if not self.initialized or not DATABASE_AVAILABLE:
            raise Exception("Database not initialized")

        with self.get_session() as session:
            result = session.execute(query, params or {})
            return [dict(row) for row in result]

# Create a singleton instance
database_client = DatabaseClient()

# Define models
if DATABASE_AVAILABLE:
    class User(Base):
        """User model."""
        __tablename__ = "users"

        id = Column(String(36), primary_key=True, index=True)
        email = Column(String(255), unique=True, index=True)
        display_name = Column(String(255), nullable=True)
        photo_url = Column(String(255), nullable=True)
        disabled = Column(Boolean, default=False)
        created_at = Column(DateTime, nullable=True)
        updated_at = Column(DateTime, nullable=True)

        # Relationships
        restaurants = relationship("Restaurant", back_populates="owner")

    class Restaurant(Base):
        """Restaurant model."""
        __tablename__ = "restaurants"

        id = Column(String(36), primary_key=True, index=True)
        name = Column(String(255), index=True)
        address = Column(String(255), nullable=True)
        city = Column(String(100), nullable=True)
        state = Column(String(100), nullable=True)
        zip_code = Column(String(20), nullable=True)
        phone = Column(String(20), nullable=True)
        website = Column(String(255), nullable=True)
        description = Column(Text, nullable=True)
        owner_id = Column(String(36), ForeignKey("users.id"))
        created_at = Column(DateTime, nullable=True)
        updated_at = Column(DateTime, nullable=True)

        # Relationships
        owner = relationship("User", back_populates="restaurants")
        foot_traffic_data = relationship("FootTrafficData", back_populates="restaurant")

    class FootTrafficData(Base):
        """Foot traffic data model."""
        __tablename__ = "foot_traffic_data"

        id = Column(String(36), primary_key=True, index=True)
        restaurant_id = Column(String(36), ForeignKey("restaurants.id"))
        date = Column(DateTime, index=True)
        total_visitors = Column(Integer)
        average_daily = Column(Integer)
        peak_hour = Column(String(50), nullable=True)
        peak_day = Column(String(50), nullable=True)
        change_percentage = Column(Float, nullable=True)
        created_at = Column(DateTime, nullable=True)
        updated_at = Column(DateTime, nullable=True)

        # Relationships
        restaurant = relationship("Restaurant", back_populates="foot_traffic_data")
        hourly_data = relationship("HourlyTrafficData", back_populates="foot_traffic")
        daily_data = relationship("DailyTrafficData", back_populates="foot_traffic")

    class HourlyTrafficData(Base):
        """Hourly traffic data model."""
        __tablename__ = "hourly_traffic_data"

        id = Column(String(36), primary_key=True, index=True)
        foot_traffic_id = Column(String(36), ForeignKey("foot_traffic_data.id"))
        hour = Column(String(10))
        visitors = Column(Integer)
        percentage = Column(Float)

        # Relationships
        foot_traffic = relationship("FootTrafficData", back_populates="hourly_data")

    class DailyTrafficData(Base):
        """Daily traffic data model."""
        __tablename__ = "daily_traffic_data"

        id = Column(String(36), primary_key=True, index=True)
        foot_traffic_id = Column(String(36), ForeignKey("foot_traffic_data.id"))
        day = Column(String(10))
        visitors = Column(Integer)
        percentage = Column(Float)

        # Relationships
        foot_traffic = relationship("FootTrafficData", back_populates="daily_data")
