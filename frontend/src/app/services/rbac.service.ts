import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Role {
    id: number;
    name: string;
    org_id: number;
    parent_role_id?: number | null;
}

@Injectable({
    providedIn: 'root'
})
export class RbacService {
    private apiUrl = `${environment.apiUrl}/rbac`;

    constructor(private http: HttpClient) { }

    getRoles(): Observable<Role[]> {
        return this.http.get<Role[]>(`${this.apiUrl}/roles`);
    }

    createRole(roleData: any): Observable<Role> {
        return this.http.post<Role>(`${this.apiUrl}/roles`, roleData);
    }

    updateRole(id: number, roleData: any): Observable<Role> {
        return this.http.put<Role>(`${this.apiUrl}/roles/${id}`, roleData);
    }

    deleteRole(id: number): Observable<Role> {
        return this.http.delete<Role>(`${this.apiUrl}/roles/${id}`);
    }
}
