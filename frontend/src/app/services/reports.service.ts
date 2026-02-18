import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TaskReport {
    id: number;
    report_type: string;
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    efficiency_score: number;
    rating: number;
    created_at: string;
}

@Injectable({
    providedIn: 'root'
})
export class ReportsService {
    private apiUrl = `${environment.apiUrl}/reports`;

    constructor(private http: HttpClient) { }

    getReports(): Observable<TaskReport[]> {
        return this.http.get<TaskReport[]>(this.apiUrl);
    }

    generateReport(type: string): Observable<TaskReport> {
        return this.http.post<TaskReport>(`${this.apiUrl}/generate?report_type=${type}`, {});
    }

    getAdminStats(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/admin-stats`);
    }
}
