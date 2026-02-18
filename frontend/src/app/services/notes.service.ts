import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Note {
    id: number;
    title: string;
    content: string;
    folder_id: number | null;
    org_id: number;
    created_by: number;
    created_at: string;
    updated_at: string;
    reminder_at?: string;
}

export interface Folder {
    id: number;
    name: string;
    org_id: number;
    created_by: number;
    created_at: string;
    notes?: Note[];
}

@Injectable({
    providedIn: 'root'
})
export class NotesService {
    private http = inject(HttpClient);
    private apiUrl = `${environment.apiUrl}/notes`;

    getFolders(): Observable<Folder[]> {
        return this.http.get<Folder[]>(`${this.apiUrl}/folders`);
    }

    createFolder(name: string): Observable<Folder> {
        return this.http.post<Folder>(`${this.apiUrl}/folders`, { name });
    }

    getNotes(params: any = {}): Observable<Note[]> {
        return this.http.get<Note[]>(this.apiUrl, { params });
    }

    getNote(id: number): Observable<Note> {
        return this.http.get<Note>(`${this.apiUrl}/${id}`);
    }

    createNote(note: Partial<Note>): Observable<Note> {
        return this.http.post<Note>(this.apiUrl, note);
    }

    updateNote(id: number, note: Partial<Note>): Observable<Note> {
        return this.http.put<Note>(`${this.apiUrl}/${id}`, note);
    }

    deleteNote(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${id}`);
    }
}
