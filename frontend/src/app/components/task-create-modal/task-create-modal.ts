import { Component, EventEmitter, Output, inject, signal, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService, Task } from '../../services/task.service';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-task-create-modal',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './task-create-modal.html',
    styleUrls: ['./task-create-modal.scss']
})
export class TaskCreateModal implements OnInit {
    private taskService = inject(TaskService);
    private authService = inject(AuthService);

    @Input() sprintId: number | null = null;
    @Output() close = new EventEmitter<void>();
    @Output() taskCreated = new EventEmitter<Task>();

    users = signal<any[]>([]);
    loading = signal(false);
    success = signal('');
    error = signal('');

    modules = ['core', 'dev', 'admin', 'net', 'sales', 'crm', 'hr', 'support'];

    newTask = {
        title: '',
        description: '',
        priority: 'Medium',
        status: 'Not Started',
        due_date: new Date().toISOString().split('T')[0],
        assignee_id: null as number | null,
        assigner_id: null as number | null,
        accountable_id: null as number | null,
        module_type: 'core',
        sprint_id: null as number | null
    };

    ngOnInit() {
        this.loadUsers();
        if (this.sprintId) {
            this.newTask.sprint_id = this.sprintId;
        }

        // Default assigner to current user
        const user = this.authService.getCurrentUser();
        if (user) {
            this.newTask.assigner_id = user.id;
        }
    }

    loadUsers() {
        this.authService.getUsers().subscribe(users => {
            this.users.set(users);
        });
    }

    onClose() {
        this.close.emit();
    }

    onSubmit() {
        if (!this.newTask.title) return;

        this.loading.set(true);
        this.success.set('');
        this.error.set('');

        this.taskService.createTask(this.newTask).subscribe({
            next: (task) => {
                this.success.set('Strategic task authorized and deployed.');
                this.loading.set(false);
                setTimeout(() => {
                    this.taskCreated.emit(task);
                    this.onClose();
                }, 1500);
            },
            error: (err) => {
                this.error.set(err.error?.detail || 'Task authorization failed. Check link stability.');
                this.loading.set(false);
            }
        });
    }
}
