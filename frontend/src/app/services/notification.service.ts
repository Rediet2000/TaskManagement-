import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Notification {
    id: number;
    message: string;
    status: string;
    trigger_event?: string;
    created_at: string;
}

@Injectable({
    providedIn: 'root'
})
export class NotificationService {
    private http = inject(HttpClient);
    private apiUrl = `${environment.apiUrl}/notifications`;

    notifications = signal<Notification[]>([]);
    unreadCount = signal<number>(0);

    loadNotifications() {
        this.http.get<Notification[]>(this.apiUrl).subscribe(notifs => {
            this.notifications.set(notifs);
            this.unreadCount.set(notifs.filter(n => n.status === 'Pending').length);
        });
    }

    markAsRead(id: number) {
        this.http.post(`${this.apiUrl}/${id}/read`, {}).subscribe(() => {
            this.loadNotifications();
        });
    }

    markAllRead() {
        this.http.post(`${this.apiUrl}/read-all`, {}).subscribe(() => {
            this.loadNotifications();
        });
    }
}
