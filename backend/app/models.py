from sqlalchemy import Column, Integer, String, Boolean
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default="employee")
    name = Column(String(255))  # ← This matches the DB column
  


class SecurityKey(Base):
    __tablename__ = "security_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    is_used = Column(Boolean, default=False)

