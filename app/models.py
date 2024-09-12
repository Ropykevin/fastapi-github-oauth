from database import Base,engine,get_db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

class StudentAccs(Base):
    __tablename__ = 'studentAcc'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    isverified = Column(Boolean, nullable=False, default=False)
    createdAt = Column(DateTime, default=func.now())


# Create all table
Base.metadata.create_all(bind=engine)
