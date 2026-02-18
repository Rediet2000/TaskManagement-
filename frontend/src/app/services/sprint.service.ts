import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Sprint {
    id: number;
    name: string;
    goal?: string;
    start_date: string;
    end_date: string;
    status: string;
    org_id: number;
    created_at: string;
}

@Injectable({
    providedIn: 'root'
})
export class SprintService {
    private apiUrl = `${environment.apiUrl}/sprints`;

    constructor(private http: HttpClient) { }

    getSprints(): Observable<Sprint[]> {
        return this.http.get<Sprint[]>(this.apiUrl);
    }

    createSprint(sprint: Partial<Sprint>): Observable<Sprint> {
        return this.http.post<Sprint>(this.apiUrl, sprint);
    }

    updateSprint(id: number, sprint: Partial<Sprint>): Observable<Sprint> {
        return this.http.put<Sprint>(`${this.apiUrl}/${id}`, sprint);
    }
}
