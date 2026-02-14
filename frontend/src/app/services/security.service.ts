import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AuditLog {
    id: number;
    user_id: number;
    action: string;
    details: string;
    timestamp: string;
}

@Injectable({
    providedIn: 'root'
})
export class SecurityService {
    private apiUrl = `${environment.apiUrl}/security`;

    constructor(private http: HttpClient) { }

    getLogs(): Observable<AuditLog[]> {
        return this.http.get<AuditLog[]>(`${this.apiUrl}/logs`);
    }

    logAction(action: string, details: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/log`, { action, details });
    }
}
