import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private currentUserSubject = new BehaviorSubject<any>(null);
    public currentUser = this.currentUserSubject.asObservable();

    constructor(private http: HttpClient) {
        const user = localStorage.getItem('currentUser');
        if (user) {
            this.currentUserSubject.next(JSON.parse(user));
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
                this.currentUserSubject.next(user);
                localStorage.setItem('currentUser', JSON.stringify(user));
            })
        );
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        this.currentUserSubject.next(null);
    }

    getToken() {
        return localStorage.getItem('token');
    }

    signup(userData: any): Observable<any> {
        return this.http.post<any>(`${environment.apiUrl}/auth/signup`, userData);
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
}
