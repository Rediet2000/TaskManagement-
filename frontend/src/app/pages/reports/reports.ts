import { Component, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TaskService, TaskReportStats } from '../../services/task.service';

@Component({
    selector: 'app-reports',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './reports.html',
    styleUrls: ['./reports.scss']
})
export class Reports implements OnInit {
    reportData = signal<TaskReportStats | null>(null);
    activeTab = signal<'overview' | 'performance'>('overview');
    loading = signal(true);

    constructor(private taskService: TaskService) { }

    ngOnInit() {
        this.loadReports();
    }

    loadReports() {
        this.loading.set(true);
        this.taskService.getTaskReports().subscribe({
            next: (data) => {
                this.reportData.set(data);
                this.loading.set(false);
            },
            error: (err) => {
                console.error('Failed to load reports', err);
                this.loading.set(false);
            }
        });
    }

    setTab(tab: 'overview' | 'performance') {
        this.activeTab.set(tab);
    }

    getCompletionPercentage(): number {
        const data = this.reportData();
        return data && data.total_tasks ? Math.round((data.completed / data.total_tasks) * 100) : 0;
    }
}
