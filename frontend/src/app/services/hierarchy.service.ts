import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Organization {
    id: number;
    name: string;
    logo_url?: string;
    primary_color: string;
    secondary_color: string;
    email_domain?: string;
    smtp_host?: string;
    smtp_port?: number;
    smtp_user?: string;
    smtp_password?: string;
    smtp_from_email?: string;

    // Password & Session Settings
    password_min_length?: number;
    password_require_special?: boolean;
    password_expiry_days?: number;
    session_timeout_minutes?: number;

    // LDAP Settings
    ldap_enabled?: boolean;
    ldap_server?: string;
    ldap_base_dn?: string;

    // Notification Settings
    telegram_bot_token?: string;
    telegram_chat_id?: string;

    // Branding Settings
    system_page_title?: string;
    theme_mode?: string;

    // Dashboard Settings
    show_dashboard_clock?: boolean;
    show_dashboard_map?: boolean;
    show_dashboard_stats?: boolean;
    show_dashboard_tasks?: boolean;
}

export interface OrganizationCreate {
    name: string;
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
    email_domain?: string;
}

export interface Branch {
    id: number;
    name: string;
    org_id: number;
    address?: string;
}

export interface Department {
    id: number;
    name: string;
}

export interface DepartmentCreate {
    name: string;
    org_id: number;
    branch_id?: number | null;
}

export interface Team {
    id: number;
    name: string;
}

@Injectable({
    providedIn: 'root'
})
export class HierarchyService {
    private apiUrl = `${environment.apiUrl}/hierarchy`;

    constructor(private http: HttpClient) { }

    getOrganization(id: number): Observable<Organization> {
        return this.http.get<Organization>(`${this.apiUrl}/organizations/${id}`);
    }

    updateOrganization(id: number, orgData: any): Observable<Organization> {
        return this.http.put<Organization>(`${this.apiUrl}/organizations/${id}`, orgData);
    }

    createOrganization(orgData: OrganizationCreate): Observable<Organization> {
        return this.http.post<Organization>(`${this.apiUrl}/organizations`, orgData);
    }

    uploadLogo(id: number, file: File): Observable<Organization> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post<Organization>(`${this.apiUrl}/organizations/${id}/logo`, formData);
    }

    getOrganizations(): Observable<Organization[]> {
        return this.http.get<Organization[]>(`${this.apiUrl}/organizations`);
    }

    // Branch methods
    getBranches(): Observable<Branch[]> {
        return this.http.get<Branch[]>(`${this.apiUrl}/branches`);
    }

    createBranch(branch: any): Observable<Branch> {
        return this.http.post<Branch>(`${this.apiUrl}/branches`, branch);
    }

    updateBranch(id: number, branch: any): Observable<Branch> {
        return this.http.put<Branch>(`${this.apiUrl}/branches/${id}`, branch);
    }

    deleteBranch(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/branches/${id}`);
    }

    getDepartments(): Observable<Department[]> {
        return this.http.get<Department[]>(`${this.apiUrl}/departments`);
    }

    getTeams(): Observable<Team[]> {
        return this.http.get<Team[]>(`${this.apiUrl}/teams`);
    }

    createDepartment(deptData: any): Observable<Department> {
        return this.http.post<Department>(`${this.apiUrl}/departments`, deptData);
    }

    createTeam(teamData: any): Observable<Team> {
        return this.http.post<Team>(`${this.apiUrl}/teams`, teamData);
    }

    getAllowedDomains(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/allowed-domains`);
    }

    createAllowedDomain(domainData: any): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/allowed-domains`, domainData);
    }

    deleteAllowedDomain(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/allowed-domains/${id}`);
    }

    testSmtp(smtpData: any): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/test-smtp`, smtpData);
    }
}
