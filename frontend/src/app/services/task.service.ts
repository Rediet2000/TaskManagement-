import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Comment {
    id: number;
    content: string;
    task_id: number;
    author_id: number;
    created_at: string;
}

export interface Attachment {
    id: number;
    file_name: string;
    file_path: string;
    file_type: string;
    file_size: number;
    task_id: number;
    uploader_id: number;
    created_at: string;
}

export interface Task {
    id: number;
    title: string;
    description?: string;
    priority: string;
    status: string;
    category?: string;
    assignee_id?: number;
    due_date?: string;
    created_at: string;
    tags: string[];
    module_type: string;
    metadata_fields: any;
    comments?: Comment[];
    attachments?: Attachment[];

    // Agile Fields
    issue_type: string;
    sprint_id?: number | null;
    parent_id?: number;
    story_points?: number;
    estimated_hours?: number;

    // Phase 11
    completed_at?: string;
    rating?: number;
    rating_comment?: string;
}

export interface UserPerformance {
    user_id: number;
    user_name: string;
    tasks_assigned: number;
    tasks_completed: number;
    tasks_started: number;
    avg_rating?: number;
    on_time_rate: number;
}

export interface TaskReportStats {
    total_tasks: number;
    unassigned: number;
    pending: number;
    completed: number;
    started: number;
    user_performance: UserPerformance[];
}

@Injectable({
    providedIn: 'root'
})
export class TaskService {
    private apiUrl = `${environment.apiUrl}/tasks`;

    constructor(private http: HttpClient) { }

    getTasks(): Observable<Task[]> {
        return this.http.get<Task[]>(this.apiUrl);
    }

    getTaskReports(): Observable<TaskReportStats> {
        return this.http.get<TaskReportStats>(`${this.apiUrl}/reports/dashboard`);
    }

    createTask(task: Partial<Task>): Observable<Task> {
        return this.http.post<Task>(this.apiUrl, task);
    }

    updateTask(id: number, task: Partial<Task>): Observable<Task> {
        return this.http.put<Task>(`${this.apiUrl}/${id}`, task);
    }

    addComment(taskId: number, content: string): Observable<Comment> {
        return this.http.post<Comment>(`${this.apiUrl}/${taskId}/comments`, { content });
    }

    getComments(taskId: number): Observable<Comment[]> {
        return this.http.get<Comment[]>(`${this.apiUrl}/${taskId}/comments`);
    }

    uploadAttachment(taskId: number, file: File): Observable<Attachment> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post<Attachment>(`${this.apiUrl}/${taskId}/attachments`, formData);
    }
}
