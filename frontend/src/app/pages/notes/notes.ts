import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NotesService, Note, Folder } from '../../services/notes.service';
import { AuthService } from '../../services/auth.service';
import { debounceTime, distinctUntilChanged, Subject } from 'rxjs';

@Component({
    selector: 'app-notes',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './notes.html',
    styleUrls: ['./notes.scss']
})
export class NotesPage implements OnInit {
    private notesService = inject(NotesService);
    private authService = inject(AuthService);

    folders = signal<Folder[]>([]);
    notes = signal<Note[]>([]);
    selectedNote = signal<Note | null>(null);
    selectedFolderId = signal<number | null>(null);
    searchQuery = signal<string>('');
    sortBy = signal<string>('updated_at');

    loading = signal<boolean>(false);
    error = signal<string>('');

    // Search subject for debouncing
    private searchSubject = new Subject<string>();

    currentUser = this.authService.currentUser;

    ngOnInit() {
        this.loadFolders();
        this.loadNotes();

        this.searchSubject.pipe(
            debounceTime(300),
            distinctUntilChanged()
        ).subscribe(query => {
            this.searchQuery.set(query);
            this.loadNotes();
        });
    }

    loadFolders() {
        this.notesService.getFolders().subscribe({
            next: (folders) => this.folders.set(folders),
            error: (err) => this.error.set('Failed to load folders')
        });
    }

    loadNotes() {
        this.loading.set(true);
        const params: any = {
            sort_by: this.sortBy(),
            order: 'desc'
        };
        if (this.selectedFolderId()) params.folder_id = this.selectedFolderId();
        if (this.searchQuery()) params.search = this.searchQuery();

        this.notesService.getNotes(params).subscribe({
            next: (notes) => {
                this.notes.set(notes);
                this.loading.set(false);
            },
            error: (err) => {
                this.error.set('Failed to load notes');
                this.loading.set(false);
            }
        });
    }

    onSearch(event: any) {
        this.searchSubject.next(event.target.value);
    }

    selectFolder(folderId: number | null) {
        this.selectedFolderId.set(folderId);
        this.loadNotes();
    }

    selectNote(note: Note) {
        this.selectedNote.set({ ...note });
    }

    createNewNote() {
        const newNote: Partial<Note> = {
            title: 'Untitled Note',
            content: '',
            folder_id: this.selectedFolderId()
        };
        this.notesService.createNote(newNote).subscribe({
            next: (note) => {
                this.notes.set([note, ...this.notes()]);
                this.selectedNote.set(note);
            }
        });
    }

    saveNote() {
        const note = this.selectedNote();
        if (!note) return;

        this.notesService.updateNote(note.id, note).subscribe({
            next: (updated) => {
                const updatedNotes = this.notes().map(n => n.id === updated.id ? updated : n);
                this.notes.set(updatedNotes);
                // If sorting by updated_at, might want to re-load to fix order
                if (this.sortBy() === 'updated_at') this.loadNotes();
            }
        });
    }

    deleteNote(id: number) {
        if (!confirm('Are you sure you want to delete this note?')) return;

        this.notesService.deleteNote(id).subscribe({
            next: () => {
                this.notes.set(this.notes().filter(n => n.id !== id));
                if (this.selectedNote()?.id === id) this.selectedNote.set(null);
            }
        });
    }

    createFolder() {
        const name = prompt('Enter folder name:');
        if (!name) return;

        this.notesService.createFolder(name).subscribe({
            next: (folder) => {
                this.folders.set([...this.folders(), folder]);
            }
        });
    }

    // Basic formatters (placeholder for real rich text editor if needed)
    formatText(type: string) {
        const textarea = document.querySelector('textarea') as HTMLTextAreaElement;
        if (!textarea) return;

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
        const selectedText = text.substring(start, end);

        let replacement = '';
        switch (type) {
            case 'bold': replacement = `**${selectedText}**`; break;
            case 'italic': replacement = `*${selectedText}*`; break;
            case 'list': replacement = `\n- ${selectedText}`; break;
            case 'numlist': replacement = `\n1. ${selectedText}`; break;
        }

        const newContent = text.substring(0, start) + replacement + text.substring(end);
        if (this.selectedNote()) {
            this.selectedNote.set({ ...this.selectedNote()!, content: newContent });
        }
    }
}
