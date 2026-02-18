import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface GitHubRepo {
    id?: number;
    github_id: number;
    name: string;
    full_name: string;
    html_url: string;
    is_private: boolean;
}

export interface GitHubIntegration {
    id: number;
    org_id: number;
    installation_id?: string;
    webhook_secret?: string;
    repositories: GitHubRepo[];
}

export interface GitHubActivity {
    id: number;
    event_type: string;
    actor: string;
    content: string;
    url?: string;
    timestamp: string;
}

@Injectable({
    providedIn: 'root'
})
export class IntegrationsService {
    private http = inject(HttpClient);
    private apiUrl = `${environment.apiUrl}/integrations`;

    getGitHubIntegration(): Observable<GitHubIntegration> {
        return this.http.get<GitHubIntegration>(`${this.apiUrl}/github`);
    }

    setupGitHubIntegration(data: Partial<GitHubIntegration>): Observable<GitHubIntegration> {
        return this.http.post<GitHubIntegration>(`${this.apiUrl}/github`, data);
    }

    registerRepository(repo: GitHubRepo): Observable<GitHubRepo> {
        return this.http.post<GitHubRepo>(`${this.apiUrl}/github/repositories`, repo);
    }

    getGitHubActivity(): Observable<GitHubActivity[]> {
        return this.http.get<GitHubActivity[]>(`${this.apiUrl}/github/activity`);
    }
}
