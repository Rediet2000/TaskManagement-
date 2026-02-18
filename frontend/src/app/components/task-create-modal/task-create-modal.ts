import { Component, EventEmitter, Output, inject, signal, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService, Task } from '../../services/task.service';
import { TranslationService } from '../../services/translation.service';
import { AuthService } from '../../services/auth.service';
import { SprintService, Sprint } from '../../services/sprint.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-task-create-modal',
    standalone: true,
    imports: [CommonModule, FormsModule, TranslatePipe],
    templateUrl: './task-create-modal.html',
    styleUrls: ['./task-create-modal.scss']
})
export class TaskCreateModal implements OnInit {
    private taskService = inject(TaskService);
    private authService = inject(AuthService);
    private sprintService = inject(SprintService);
    private translationService = inject(TranslationService);

    @Input() sprintId: number | null = null;
    @Output() close = new EventEmitter<void>();
    @Output() taskCreated = new EventEmitter<Task>();

    users = signal<any[]>([]);
    sprints = signal<Sprint[]>([]);
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
        this.loadSprints();
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

    loadSprints() {
        this.sprintService.getSprints().subscribe(sprints => {
            this.sprints.set(sprints);
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
                this.success.set(this.translationService.translate('STRATEGIC_TASK_AUTHORIZED'));
                this.loading.set(false);
                setTimeout(() => {
                    this.taskCreated.emit(task);
                    this.onClose();
                }, 1500);
            },
            error: (err) => {
                this.error.set(err.error?.detail || this.translationService.translate('TASK_AUTH_FAILED'));
                this.loading.set(false);
            }
        });
    }
}
