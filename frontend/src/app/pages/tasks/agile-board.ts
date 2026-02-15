import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService, Task } from '../../services/task.service';
import { SprintService, Sprint } from '../../services/sprint.service';
import { DragDropModule, CdkDragDrop } from '@angular/cdk/drag-drop';
import { TaskCreateModal } from '../../components/task-create-modal/task-create-modal';
import { BoardService, Board, BoardColumn } from '../../services/board.service';

@Component({
    selector: 'app-agile-board',
    standalone: true,
    imports: [CommonModule, FormsModule, DragDropModule, TaskCreateModal],
    templateUrl: './agile-board.html',
    styleUrls: ['./agile-board.scss']
})
export class AgileBoard implements OnInit {
    tasks = signal<Task[]>([]);
    sprints = signal<Sprint[]>([]);
    activeSprint = signal<Sprint | null>(null);
    boards = signal<Board[]>([]);
    activeBoard = signal<Board | null>(null);
    loading = signal(false);

    showBoardModal = signal(false);
    showSprintModal = signal(false);
    showTaskModal = signal(false);
    newSprint = {
        name: '',
        goal: '',
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    };
    newBoard = {
        name: '',
        type: 'kanban' as 'kanban' | 'scrum',
        description: ''
    };

    constructor(
        private taskService: TaskService,
        private sprintService: SprintService,
        private boardService: BoardService
    ) { }

    ngOnInit() {
        this.loadData();
    }

    loadData() {
        this.loading.set(true);
        this.boardService.getBoards().subscribe(boards => {
            this.boards.set(boards);
            if (boards.length > 0 && !this.activeBoard()) {
                this.activeBoard.set(boards[0]);
            }
            this.loadSprints();
        });
    }

    loadSprints() {
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
        return this.tasks().filter(t => !t.sprint_id && (!this.activeBoard() || t.board_id === this.activeBoard()?.id));
    }

    get activeColumns(): BoardColumn[] {
        return this.activeBoard()?.columns || [];
    }

    get agileColumnNames(): string[] {
        return this.activeColumns.map(c => c.name);
    }

    getSprintTasksByColumn(column: BoardColumn) {
        if (!this.activeSprint()) return [];
        return this.tasks().filter(t =>
            t.sprint_id === this.activeSprint()?.id &&
            (t.board_column_id === column.id || t.status === (column.status_mapping || column.name))
        );
    }

    getColumnWipLimit(column: BoardColumn): number | null {
        return column.wip_limit || null;
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

    onCreateBoard() {
        this.boardService.createBoard(this.newBoard).subscribe(board => {
            this.loadData();
            this.activeBoard.set(board);
            this.showBoardModal.set(false);
        });
    }

    onTaskCreated() {
        this.loadTasks();
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

    transitionSprint(status: string) {
        if (!this.activeSprint()) return;
        const id = this.activeSprint()!.id;
        this.sprintService.updateSprint(id, { status }).subscribe(() => {
            this.loadData();
        });
    }

    onDrop(event: CdkDragDrop<Task[]>) {
        const task = event.item.data;
        const targetId = event.container.id;

        if (event.previousContainer === event.container) return;

        if (targetId === 'backlog') {
            const updatePayload = { sprint_id: null, board_column_id: null };
            this.performTaskUpdate(task, updatePayload);
            return;
        }

        const targetColumn = this.activeBoard()?.columns.find(c => c.name === targetId);
        if (targetColumn) {
            // WIP Limit Validation (Soft warning for now)
            const currentCount = this.getSprintTasksByColumn(targetColumn).length;
            if (targetColumn.wip_limit && currentCount >= targetColumn.wip_limit) {
                console.warn(`WIP limit reached for ${targetId}`);
            }

            const updatePayload = {
                sprint_id: this.activeSprint()?.id,
                board_id: this.activeBoard()?.id,
                board_column_id: targetColumn.id,
                status: targetColumn.status_mapping || targetId
            };
            this.performTaskUpdate(task, updatePayload);
        }
    }

    private performTaskUpdate(task: Task, payload: Partial<Task>) {
        this.tasks.update(tasks => tasks.map(t => t.id === task.id ? { ...t, ...payload } : t));
        this.taskService.updateTask(task.id, payload).subscribe({
            error: () => this.loadTasks()
        });
    }

    onBoardChange(boardId: any) {
        const id = Number(boardId);
        const board = this.boards().find(b => b.id === id);
        if (board) {
            this.activeBoard.set(board);
            this.loadTasks();
        }
    }

    onArchiveTask(task: Task) {
        this.taskService.archiveTask(task.id).subscribe({
            next: () => this.loadTasks(),
            error: (err) => console.error('Failed to archive task', err)
        });
    }
}
