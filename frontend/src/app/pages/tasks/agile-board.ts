import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService, Task } from '../../services/task.service';
import { SprintService, Sprint } from '../../services/sprint.service';
import { DragDropModule, CdkDragDrop } from '@angular/cdk/drag-drop';

@Component({
    selector: 'app-agile-board',
    standalone: true,
    imports: [CommonModule, FormsModule, DragDropModule],
    templateUrl: './agile-board.html',
    styleUrls: ['./agile-board.scss']
})
export class AgileBoard implements OnInit {
    tasks = signal<Task[]>([]);
    sprints = signal<Sprint[]>([]);
    activeSprint = signal<Sprint | null>(null);
    loading = signal(false);

    showSprintModal = signal(false);
    newSprint = {
        name: '',
        goal: '',
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    };

    constructor(
        private taskService: TaskService,
        private sprintService: SprintService
    ) { }

    ngOnInit() {
        this.loadData();
    }

    loadData() {
        this.loading.set(true);
        this.sprintService.getSprints().subscribe(sprints => {
            this.sprints.set(sprints);
            const active = sprints.find(s => s.status === 'Active');
            if (active) this.activeSprint.set(active);
            this.loadTasks();
        });
    }

    loadTasks() {
        this.taskService.getTasks().subscribe(tasks => {
            this.tasks.set(tasks);
            this.loading.set(false);
        });
    }

    getBacklogTasks() {
        return this.tasks().filter(t => !t.sprint_id);
    }

    getSprintTasks() {
        if (!this.activeSprint()) return [];
        return this.tasks().filter(t => t.sprint_id === this.activeSprint()?.id);
    }

    onSprintChange(sprintId: any) {
        // Convert string to number if needed (select value might be string)
        const id = Number(sprintId);
        const sprint = this.sprints().find(s => s.id === id);
        if (sprint) {
            this.activeSprint.set(sprint);
        }
    }

    onCreateSprint() {
        this.sprintService.createSprint(this.newSprint).subscribe(() => {
            this.loadData();
            this.showSprintModal.set(false);
        });
    }

    onMoveToSprint(task: Task) {
        if (!this.activeSprint()) return;
        const sprintId = this.activeSprint()!.id;

        this.tasks.update(tasks => tasks.map(t =>
            t.id === task.id ? { ...t, sprint_id: sprintId } : t
        ));

        this.taskService.updateTask(task.id, { sprint_id: sprintId }).subscribe({
            error: () => this.loadTasks()
        });
    }

    onMoveToBacklog(task: Task) {
        this.tasks.update(tasks => tasks.map(t =>
            t.id === task.id ? { ...t, sprint_id: null } : t
        ));

        this.taskService.updateTask(task.id, { sprint_id: null }).subscribe({
            error: () => this.loadTasks()
        });
    }

    onDrop(event: CdkDragDrop<Task[]>) {
        if (event.previousContainer === event.container) return;

        const task = event.item.data;
        const targetId = event.container.id;
        const newSprintId = targetId === 'active-sprint' ? (this.activeSprint()?.id || null) : null;

        if (targetId === 'active-sprint' && !this.activeSprint()) return;

        // Optimistic UI update using Signal immutable pattern
        this.tasks.update(tasks => tasks.map(t =>
            t.id === task.id ? { ...t, sprint_id: newSprintId } : t
        ));

        this.taskService.updateTask(task.id, { sprint_id: newSprintId }).subscribe({
            error: () => this.loadTasks() // Revert on error
        });
    }
}
