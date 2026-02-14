import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

import { toObservable } from '@angular/core/rxjs-interop';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    public currentUser = signal<any>(null);
    public isInitialized = signal<boolean>(false);
    public currentUser$ = toObservable(this.currentUser);

    constructor(private http: HttpClient) {
        const user = localStorage.getItem('currentUser');
        const token = localStorage.getItem('token');

        if (user) {
            this.currentUser.set(JSON.parse(user));
        }

        if (token) {
            this.getMe().subscribe({
                next: () => this.isInitialized.set(true),
                error: () => {
                    this.logout();
                    this.isInitialized.set(true);
                }
            });
        } else {
            this.isInitialized.set(true);
        }
    }

    login(email: string, password: string): Observable<any> {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        return this.http.post<any>(`${environment.apiUrl}/auth/login/access-token`, formData).pipe(
            tap(response => {
                localStorage.setItem('token', response.access_token);
            })
        );
    }

    getMe(): Observable<any> {
        return this.http.get<any>(`${environment.apiUrl}/auth/me`).pipe(
            tap(user => {
                this.currentUser.set(user);
                localStorage.setItem('currentUser', JSON.stringify(user));
            })
        );
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        this.currentUser.set(null);
    }

    getToken() {
        return localStorage.getItem('token');
    }

    getCurrentUser(): any {
        return this.currentUser();
    }

    signup(userData: any): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/signup`, userData);
    }

    registerCompany(data: any): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/register-company`, data).pipe(
            tap(response => {
                localStorage.setItem('token', response.access_token);
                // We need to fetch user details immediately after
                this.getMe().subscribe();
            })
        );
    }

    requestPasswordReset(email: string): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/password-reset-request`, { email });
    }

    confirmPasswordReset(data: any): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/password-reset-confirm`, data);
    }

    getUsers(): Observable<any[]> {
        return this.http.get<any[]>(`${environment.apiUrl}/auth/users`);
    }

    toggleUserStatus(userId: number): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/users/${userId}/toggle-status`, {});
    }

    updateUser(userId: number, userData: any): Observable<any> {
        return this.http.put<any>(`${environment.apiUrl}/auth/users/${userId}`, userData);
    }

    hasPermission(requiredPermission: string): boolean {
        const user = this.currentUser();
        if (!user) return false;

        // Admin Bypass
        if (user.role_name === 'Admin' || user.role_name === 'Super Admin') return true;

        if (!user.permissions || !Array.isArray(user.permissions)) return false;
        return user.permissions.includes(requiredPermission);
    }

    inviteUser(data: any): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/invite`, data);
    }

    getInvitation(token: string): Observable<any> {
        return this.http.get<any>(`${environment.apiUrl}/auth/invitation/${token}`);
    }

    suspendUser(userId: number): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/users/${userId}/suspend`, {});
    }

    // Profile Management
    getProfile(): Observable<any> {
        return this.http.get<any>(`${environment.apiUrl}/profile/me`);
    }

    updateProfile(data: any): Observable<any> {
        return this.http.put<any>(`${environment.apiUrl}/profile/me`, data);
    }

    uploadProfilePhoto(file: File): Observable<any> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post<any>(`${environment.apiUrl}/profile/photo`, formData);
    }

    deleteProfilePhoto(): Observable<any> {
        return this.http.delete<any>(`${environment.apiUrl}/profile/photo`);
    }

    changePassword(data: any): Observable<any> {
        return this.http.put<any>(`${environment.apiUrl}/profile/password`, data);
    }

    getActivitySnapshot(): Observable<any> {
        return this.http.get<any>(`${environment.apiUrl}/profile/activity`);
    }

    updateNotificationSettings(settings: any): Observable<any> {
        return this.http.put<any>(`${environment.apiUrl}/profile/notifications`, settings);
    }

    enable2FA(): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/profile/2fa/enable`, {});
    }

    disable2FA(): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/profile/2fa/disable`, {});
    }
}
