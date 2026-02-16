import { Component, OnInit, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService, Task } from '../../services/task.service';
import { AuthService } from '../../services/auth.service';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, ActivatedRoute } from '@angular/router';
import { DragDropModule, CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { toSignal } from '@angular/core/rxjs-interop';

import { HasPermissionDirective } from '../../directives/has-permission.directive';
import { TaskCreateModal } from '../../components/task-create-modal/task-create-modal';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-task-board',
    standalone: true,
    imports: [CommonModule, FormsModule, DragDropModule, HasPermissionDirective, TaskCreateModal, TranslatePipe],
    templateUrl: './task-board.html',
    styleUrls: ['./task-board.scss']
})
export class TaskBoard implements OnInit {
    private taskService = inject(TaskService);
    private authService = inject(AuthService);
    private route = inject(ActivatedRoute);
    private router = inject(Router);

    currentUser = this.authService.currentUser;

    tasks = signal<Task[]>([]);
    columns = ['Not Started', 'Started', 'Pending', 'Completed'];

    showModal = signal(false);
    showDetails = signal(false);
    selectedTask = signal<Task | null>(null);
    newComment = '';
    newTag = '';
    users = signal<any[]>([]);
    canEditTask = computed(() => this.authService.hasPermission('task.edit'));
    modules = ['core', 'dev', 'admin', 'net', 'sales', 'crm', 'hr', 'support'];

    updateTaskField(field: string, value: any) {
        if (!this.selectedTask()) return;
        const taskId = this.selectedTask()!.id;

        const updatePayload = { [field]: value };

        // Optimistic update
        this.selectedTask.set({ ...this.selectedTask()!, ...updatePayload });
        this.tasks.update(tasks => tasks.map(t => t.id === taskId ? { ...t, ...updatePayload } : t));

        this.taskService.updateTask(taskId, updatePayload).subscribe({
            error: (err) => {
                console.error('Failed to update task field', err);
                this.loadTasks(); // Revive on error
            }
        });
    }

    ngOnInit() {
        this.route.queryParamMap.subscribe(params => {
            const searchTerm = params.get('search');
            this.loadTasks(searchTerm || undefined);
        });
        this.loadUsers();
    }

    loadTasks(search?: string) {
        this.taskService.getTasks(search).subscribe((tasks: Task[]) => {
            this.tasks.set(tasks);
        });
    }

    loadUsers() {
        this.authService.getUsers().subscribe(users => {
            this.users.set(users);
        });
    }

    getTasksByStatus(status: string) {
        return this.tasks().filter((t: Task) => t.status === status);
    }

    onDrop(event: CdkDragDrop<Task[]>) {
        if (event.previousContainer === event.container) {
            const status = event.container.id;
            const columnTasks = this.getTasksByStatus(status);
            moveItemInArray(columnTasks, event.previousIndex, event.currentIndex);
            // Note: Reordering within same column isn't persisted yet as our API 
            // doesn't have a 'position' field, but this keeps the UI stable.
        } else {
            const task = event.item.data;
            const newStatus = event.container.id;

            // Optimistic UI update using Signal immutable pattern
            this.tasks.update(tasks => tasks.map(t =>
                t.id === task.id ? { ...t, status: newStatus } : t
            ));

            this.taskService.updateTask(task.id, { status: newStatus }).subscribe({
                error: () => this.loadTasks() // Revert on error
            });
        }
    }

    getUserName(userId?: number | null): string {
        if (!userId) return 'Unassigned';
        const user = this.users().find(u => u.id === userId);
        return user ? (user.full_name || user.email) : 'Unknown User';
    }

    getUserInitial(userId?: number | null): string {
        if (!userId) return '?';
        const user = this.users().find(u => u.id === userId);
        if (!user) return '?';
        const name = user.full_name || user.email;
        return name.charAt(0).toUpperCase();
    }

    onTaskCreated() {
        this.loadTasks();
    }

    onSelectTask(task: Task) {
        this.taskService.getTask(task.id).subscribe(fullTask => {
            this.selectedTask.set(fullTask);
            this.showDetails.set(true);
            this.loadComments(task.id);
        });
    }

    loadComments(taskId: number) {
        this.taskService.getComments(taskId).subscribe(comments => {
            const current = this.selectedTask();
            if (current && current.id === taskId) {
                this.selectedTask.set({ ...current, comments });
            }
        });
    }

    onAddComment() {
        if (!this.newComment.trim() || !this.selectedTask()) return;
        this.taskService.addComment(this.selectedTask()!.id, this.newComment).subscribe(() => {
            this.loadComments(this.selectedTask()!.id);
            this.newComment = '';
        });
    }

    onUploadFile(event: any) {
        const file = event.target.files[0];
        if (file && this.selectedTask()) {
            this.taskService.uploadAttachment(this.selectedTask()!.id, file).subscribe(() => {
                this.loadTasks(); // To refresh attachment count/list
            });
        }
    }

    addTag() {
        if (this.newTag.trim() && this.selectedTask()) {
            const task = this.selectedTask()!;
            const tags = [...(task.tags || []), this.newTag.trim()];
            console.log('DEBUG: Adding tag', this.newTag, 'Current tags:', task.tags);
            this.taskService.updateTask(task.id, { tags }).subscribe({
                next: () => {
                    console.log('DEBUG: Tag added successfully');
                    this.selectedTask.set({ ...task, tags });
                    this.loadTasks();
                    this.newTag = '';
                },
                error: (err) => console.error('DEBUG: Failed to add tag', err)
            });
        } else {
            console.warn('DEBUG: Cannot add tag - empty or no task selected');
        }
    }

    removeTag(tag: string) {
        if (this.selectedTask()) {
            const task = this.selectedTask()!;
            const tags = task.tags.filter(t => t !== tag);
            this.taskService.updateTask(task.id, { tags }).subscribe(() => {
                this.selectedTask.set({ ...task, tags });
                this.loadTasks();
            });
        }
    }


    canRateTask(): boolean {
        const user = this.currentUser() as any;
        // Allow Admins and Managers to rate
        // Note: API returns 'role_name', not 'role'
        const role = user?.role_name || user?.role;
        const allowedRoles = ['Admin', 'Manager', 'Administrator', 'Super Admin'];

        console.log('DEBUG: canRateTask', { userRole: role, allowed: allowedRoles.includes(role) });
        return allowedRoles.includes(role);
    }

    rateTask(rating: number) {
        console.log('DEBUG: rateTask clicked', rating);
        if (this.selectedTask()) {
            if (!this.canRateTask()) {
                console.warn('DEBUG: Rating denied - permission check failed');
                return;
            }

            const task = this.selectedTask()!;
            this.taskService.updateTask(task.id, { rating }).subscribe({
                next: () => {
                    console.log('DEBUG: Rating success');
                    this.selectedTask.set({ ...task, rating });
                    // Optimistically update the list
                    this.tasks.update(tasks => tasks.map(t => t.id === task.id ? { ...t, rating } : t));
                },
                error: (err) => console.error('DEBUG: Rating failed', err)
            });
        } else {
            console.warn('DEBUG: No task selected');
        }
    }

    onArchiveTask() {
        if (!this.selectedTask()) return;
        const taskId = this.selectedTask()!.id;
        this.taskService.archiveTask(taskId).subscribe({
            next: () => {
                this.showDetails.set(false);
                this.loadTasks();
            },
            error: (err) => console.error('Failed to archive task', err)
        });
    }
}
