from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database connection setup
engine = create_engine("sqlite:///./knowmap.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Relationship with profile
    profile = relationship("UserProfile", back_populates="user", uselist=False)

# Profile Table - FIXED
class UserProfile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    interests = Column(String, default="")
    saved_graphs = Column(String, default="")
    
    # Relationship with user
    user = relationship("User", back_populates="profile")

# Create tables
print("🔄 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")