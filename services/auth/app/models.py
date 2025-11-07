from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    hashed_password = Column(String)
    job_title = Column(String, nullable=False)


class DefectStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress" 
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class DefectPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    defects = relationship("Defect", back_populates="project")



class Defect(Base):
    __tablename__ = "defects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="new")
    priority = Column(String, default="medium")

    project_id = Column(Integer, ForeignKey("projects.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))

    due_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="defects")
    comments = relationship("Comment", back_populates="defect")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    defect_id = Column(Integer, ForeignKey("defects.id"))
    author_id = Column(String, ForeignKey("users.name"))
    created_at = Column(DateTime, default=func.now())

    defect = relationship("Defect", back_populates="comments")



class ProjectHistory(Base):
    __tablename__ = "project_history"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    defect_id = Column(Integer, ForeignKey("defects.id"))
    changed_by = Column(Integer, ForeignKey("users.id"))
    change_type = Column(String, nullable=False)  # 'defect_created', 'defect_updated'
    field_name = Column(String)                   # Название измененного поля
    old_value = Column(Text)                      # Старое значение
    new_value = Column(Text)                      # Новое значение
    change_date = Column(DateTime, default=func.now())
    
    # Связи
    project = relationship("Project")
    defect = relationship("Defect")
    user = relationship("User")
