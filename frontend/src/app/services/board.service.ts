import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface BoardColumn {
    id: number;
    board_id: number;
    name: string;
    position: number;
    wip_limit?: number;
    status_mapping?: string;
}

export interface Board {
    id: number;
    name: string;
    description?: string;
    type: 'kanban' | 'scrum';
    org_id: number;
    project_id?: number;
    created_at: string;
    is_active: boolean;
    columns: BoardColumn[];
}

@Injectable({
    providedIn: 'root'
})
export class BoardService {
    private apiUrl = `${environment.apiUrl}/agile`;

    constructor(private http: HttpClient) { }

    getBoards(): Observable<Board[]> {
        return this.http.get<Board[]>(this.apiUrl);
    }

    getBoard(id: number): Observable<Board> {
        return this.http.get<Board>(`${this.apiUrl}/${id}`);
    }

    createBoard(board: Partial<Board>): Observable<Board> {
        return this.http.post<Board>(this.apiUrl, board);
    }

    updateBoard(id: number, board: Partial<Board>): Observable<Board> {
        return this.http.put<Board>(`${this.apiUrl}/${id}`, board);
    }

    addColumn(boardId: number, column: Partial<BoardColumn>): Observable<BoardColumn> {
        return this.http.post<BoardColumn>(`${this.apiUrl}/${boardId}/columns`, column);
    }

    updateColumn(columnId: number, column: Partial<BoardColumn>): Observable<BoardColumn> {
        return this.http.put<BoardColumn>(`${this.apiUrl}/columns/${columnId}`, column);
    }

    deleteColumn(columnId: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/columns/${columnId}`);
    }
}
