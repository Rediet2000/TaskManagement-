from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class TaskReportBase(BaseModel):
    org_id: int
    user_id: int
    report_type: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    efficiency_score: float
    rating: int
    start_date: datetime
    end_date: datetime

class TaskReportCreate(TaskReportBase):
    pass

class TaskReport(TaskReportBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DepartmentEfficiency(BaseModel):
    name: str
    score: float

class SectorPerformance(BaseModel):
    rank: int
    name: str
    score: str # e.g. "99.1% Opti-Rate"

class RealTimeInsights(BaseModel):
    diagnostic_performance: List[float]
    department_ranking: List[DepartmentEfficiency]
    sector_performance: List[SectorPerformance]
