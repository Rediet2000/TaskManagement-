import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService, Task } from '../../services/task.service';

@Component({
    selector: 'app-task-board',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './task-board.html',
    styleUrls: ['./task-board.scss']
})
export class TaskBoard implements OnInit {
    tasks = signal<Task[]>([]);
    columns = ['Not Started', 'Started', 'Pending', 'Completed'];

    showModal = signal(false);
    newTask = {
        title: '',
        description: '',
        priority: 'Medium',
        status: 'Not Started',
        due_date: new Date().toISOString().split('T')[0]
    };

    constructor(private taskService: TaskService) { }

    ngOnInit() {
        this.loadTasks();
    }

    loadTasks() {
        this.taskService.getTasks().subscribe((tasks: Task[]) => {
            this.tasks.set(tasks);
        });
    }

    getTasksByStatus(status: string) {
        return this.tasks().filter((t: Task) => t.status === status);
    }

    onAddTask() {
        this.taskService.createTask(this.newTask).subscribe({
            next: () => {
                this.loadTasks();
                this.showModal.set(false);
                this.resetNewTask();
            },
            error: (err: any) => console.error('Failed to create task', err)
        });
    }

    resetNewTask() {
        this.newTask = {
            title: '',
            description: '',
            priority: 'Medium',
            status: 'Not Started',
            due_date: new Date().toISOString().split('T')[0]
        };
    }
}
