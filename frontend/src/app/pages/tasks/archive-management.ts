import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService, Task } from '../../services/task.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-archive-management',
    standalone: true,
    imports: [CommonModule, FormsModule, TranslatePipe],
    templateUrl: './archive-management.html',
    styleUrls: ['./archive-management.scss']
})
export class ArchiveManagement implements OnInit {
    private taskService = inject(TaskService);

    archivedTasks = signal<Task[]>([]);
    loading = signal(false);
    error = signal('');
    success = signal('');

    ngOnInit() {
        this.loadArchivedTasks();
    }

    loadArchivedTasks() {
        this.loading.set(true);
        this.taskService.getTasks('', true).subscribe({
            next: (tasks: Task[]) => {
                this.archivedTasks.set(tasks.filter(t => (t as any).is_archived));
                this.loading.set(false);
            },
            error: (err: any) => {
                this.error.set('Failed to load mission archives.');
                this.loading.set(false);
            }
        });
    }

    onRestore(task: Task) {
        this.taskService.unarchiveTask(task.id).subscribe({
            next: () => {
                this.success.set(`Mission '${task.title}' restored to active duty.`);
                this.loadArchivedTasks();
                setTimeout(() => this.success.set(''), 3000);
            },
            error: () => {
                this.error.set('Failed to restore mission.');
                setTimeout(() => this.error.set(''), 3000);
            }
        });
    }
}
