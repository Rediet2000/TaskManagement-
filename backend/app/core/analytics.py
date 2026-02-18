import pandas as pd
from sqlalchemy.orm import Session
from app.models.task_tracking import Task, ProblemArea
from app.models.core import User
from datetime import datetime, timedelta

class AnalyticsEngine:
    @staticmethod
    def get_realtime_insights(db: Session, org_id: int):
        from app.models.core import Department, Branch, Team
        from app.models.task_tracking import Task
        from sqlalchemy import func
        from datetime import datetime, timedelta

        # 1. Diagnostic Performance (10-Day Trend)
        today = datetime.now()
        trend_data = []
        for i in range(9, -1, -1):
            date = today - timedelta(days=i)
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            count = db.query(Task).filter(
                Task.org_id == org_id,
                Task.completed_at >= start_of_day,
                Task.completed_at <= end_of_day
            ).count()
            # Normalize for a 0-100 scale in the UI chart
            # If there are few tasks, we'll scale it so it looks dynamic
            trend_data.append(float(min(count * 10, 100)))

        # 2. Department Efficiency Ranking
        depts = db.query(Department).filter(Department.org_id == org_id).all()
        dept_ranking = []
        for d in depts:
            total_tasks = db.query(Task).join(Team).filter(
                Team.dept_id == d.id,
                Task.org_id == org_id
            ).count()
            
            completed_tasks = db.query(Task).join(Team).filter(
                Team.dept_id == d.id,
                Task.org_id == org_id,
                Task.status == "Completed"
            ).count()
            
            score = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            dept_ranking.append({"name": d.name, "score": round(score, 1)})
        
        # Sort by score descending
        dept_ranking.sort(key=lambda x: x["score"], reverse=True)

        # 3. Sector (Branch) Performance Protocols
        branches = db.query(Branch).filter(Branch.org_id == org_id).all()
        sector_performance = []
        for i, b in enumerate(branches):
            # Calculate Opti-Rate based on all tasks in the branch (tasks connected via teams/departments)
            total_tasks = db.query(Task).join(Team).join(Department).filter(
                Department.branch_id == b.id,
                Task.org_id == org_id
            ).count()
            
            completed_tasks = db.query(Task).join(Team).join(Department).filter(
                Department.branch_id == b.id,
                Task.org_id == org_id,
                Task.status == "Completed"
            ).count()
            
            rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            sector_performance.append({
                "rank": i + 1,
                "name": b.name,
                "score": f"{round(rate, 1)}% Opti-Rate"
            })
            
        # Re-rank after sorting
        sector_performance.sort(key=lambda x: float(x["score"].split('%')[0]), reverse=True)
        for i, s in enumerate(sector_performance):
            s["rank"] = i + 1

        return {
            "diagnostic_performance": trend_data,
            "department_ranking": dept_ranking[:4], # Top 4
            "sector_performance": sector_performance[:4] # Top 4
        }
