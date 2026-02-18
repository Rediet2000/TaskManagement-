from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
import enum

class BoardType(str, enum.Enum):
    KANBAN = "kanban"
    SCRUM = "scrum"

class BoardColumnBase(BaseModel):
    name: str
    position: int = 0
    wip_limit: Optional[int] = None
    status_mapping: Optional[str] = None

class BoardColumnCreate(BoardColumnBase):
    pass

class BoardColumnUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None
    wip_limit: Optional[int] = None
    status_mapping: Optional[str] = None

class BoardColumn(BoardColumnBase):
    id: int
    board_id: int
    model_config = ConfigDict(from_attributes=True)

class BoardBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: BoardType = BoardType.KANBAN
    project_id: Optional[int] = None

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[BoardType] = None
    project_id: Optional[int] = None
    is_active: Optional[bool] = None

class Board(BoardBase):
    id: int
    org_id: int
    created_at: datetime
    is_active: bool
    columns: List[BoardColumn] = []
    model_config = ConfigDict(from_attributes=True)
