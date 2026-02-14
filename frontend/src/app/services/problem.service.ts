import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ProblemArea {
    id: number;
    branch_location: string;
    component?: string;
    device_id?: string;
    problem_type: string;
    severity?: string;
    status: string;
    assigned_date: string;
    resolution_time?: number;
}

@Injectable({
    providedIn: 'root'
})
export class ProblemService {
    private apiUrl = `${environment.apiUrl}/problems`;

    constructor(private http: HttpClient) { }

    getProblems(): Observable<ProblemArea[]> {
        return this.http.get<ProblemArea[]>(this.apiUrl);
    }

    createProblem(problem: any): Observable<ProblemArea> {
        return this.http.post<ProblemArea>(this.apiUrl, problem);
    }

    fixProblem(id: number): Observable<ProblemArea> {
        return this.http.patch<ProblemArea>(`${this.apiUrl}/${id}/fix`, {});
    }
}
