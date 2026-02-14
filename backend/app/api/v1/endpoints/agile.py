from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.agile import Board, BoardColumn
from app.models.task_tracking import Task, Sprint
from app.schemas.agile import Board as BoardSchema, BoardCreate, BoardUpdate, BoardColumn as ColumnSchema, BoardColumnCreate, BoardColumnUpdate
from app.db.base import get_db

router = APIRouter()

@router.get("/", response_model=List[BoardSchema])
def read_boards(
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve boards."""
    boards = db.query(Board).filter(Board.org_id == current_user.org_id).offset(skip).limit(limit).all()
    return boards

@router.post("/", response_model=BoardSchema)
def create_board(
    *,
    db: Session = Depends(get_db),
    board_in: BoardCreate,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Create new board."""
    board = Board(
        **board_in.model_dump(),
        org_id=current_user.org_id
    )
    db.add(board)
    db.flush() # To get board ID for default columns

    # Create default columns
    default_columns = [
        {"name": "To Do", "position": 0, "status_mapping": "Not Started"},
        {"name": "In Progress", "position": 1, "status_mapping": "Started"},
        {"name": "Done", "position": 2, "status_mapping": "Completed"},
    ]
    for col_data in default_columns:
        col = BoardColumn(**col_data, board_id=board.id)
        db.add(col)
    
    db.commit()
    db.refresh(board)
    return board

@router.get("/{board_id}", response_model=BoardSchema)
def read_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Get board by ID."""
    board = db.query(Board).filter(Board.id == board_id, Board.org_id == current_user.org_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("/{board_id}", response_model=BoardSchema)
def update_board(
    *,
    db: Session = Depends(get_db),
    board_id: int,
    board_in: BoardUpdate,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Update a board."""
    board = db.query(Board).filter(Board.id == board_id, Board.org_id == current_user.org_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    update_data = board_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(board, field, value)
    
    db.commit()
    db.refresh(board)
    return board

# Column Endpoints
@router.post("/{board_id}/columns", response_model=ColumnSchema)
def create_column(
    *,
    db: Session = Depends(get_db),
    board_id: int,
    column_in: BoardColumnCreate,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Add a column to a board."""
    board = db.query(Board).filter(Board.id == board_id, Board.org_id == current_user.org_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    column = BoardColumn(**column_in.model_dump(), board_id=board_id)
    db.add(column)
    db.commit()
    db.refresh(column)
    return column

@router.put("/columns/{column_id}", response_model=ColumnSchema)
def update_column(
    *,
    db: Session = Depends(get_db),
    column_id: int,
    column_in: BoardColumnUpdate,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Update a column."""
    column = db.query(BoardColumn).join(Board).filter(
        BoardColumn.id == column_id, 
        Board.org_id == current_user.org_id
    ).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    update_data = column_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(column, field, value)
    
    db.commit()
    db.refresh(column)
    return column

@router.delete("/columns/{column_id}")
def delete_column(
    column_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Delete a column."""
    column = db.query(BoardColumn).join(Board).filter(
        BoardColumn.id == column_id, 
        Board.org_id == current_user.org_id
    ).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    db.delete(column)
    db.commit()
    return {"message": "Column deleted successfully"}
