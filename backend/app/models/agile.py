from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class BoardType(str, enum.Enum):
    KANBAN = "kanban"
    SCRUM = "scrum"

class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    type = Column(String, default=BoardType.KANBAN)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    project_id = Column(Integer, nullable=True) # For future project-based grouping
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization")
    columns = relationship("BoardColumn", back_populates="board", cascade="all, delete-orphan", order_by="BoardColumn.position")
    tasks = relationship("Task", back_populates="board")
    sprints = relationship("Sprint", back_populates="board")

class BoardColumn(Base):
    __tablename__ = "board_columns"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"))
    name = Column(String)
    position = Column(Integer, default=0)
    wip_limit = Column(Integer, nullable=True)
    status_mapping = Column(String, nullable=True) # maps to TaskStatus enum name

    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="board_column")
