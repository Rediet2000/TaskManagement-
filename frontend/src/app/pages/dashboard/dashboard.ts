import { Component, signal, inject, OnInit, OnDestroy, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../../services/theme.service';
import { HierarchyService, Branch } from '../../services/hierarchy.service';
import { TaskCreateModal } from '../../components/task-create-modal/task-create-modal';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, TaskCreateModal],
    templateUrl: './dashboard.html',
    styleUrls: ['./dashboard.scss']
})
export class Dashboard implements OnInit, OnDestroy {
    private themeService = inject(ThemeService);
    private hierarchyService = inject(HierarchyService);

    currentOrg = this.themeService.currentOrg;

    currentTime = signal(new Date());
    branches = signal<Branch[]>([]);
    showTaskModal = signal(false);
    private timer: any;
    private refreshTimer: any;

    // Analog clock rotations
    secondRotation = computed(() => this.currentTime().getSeconds() * 6);
    minuteRotation = computed(() => this.currentTime().getMinutes() * 6 + this.currentTime().getSeconds() * 0.1);
    hourRotation = computed(() => (this.currentTime().getHours() % 12) * 30 + this.currentTime().getMinutes() * 0.5);

    stats = computed(() => [
        {
            label: 'Total Tasks',
            value: this.rawStats().total_tasks.toString(),
            icon: 'bi-list-task',
            trend: '+12%',
            trendUp: true
        },
        {
            label: 'Active Tasks',
            value: this.rawStats().active_tasks.toString(),
            icon: 'bi-play-circle',
            trend: '+5%',
            trendUp: true
        },
        {
            label: 'Overdue',
            value: this.rawStats().overdue_tasks.toString(),
            icon: 'bi-exclamation-triangle',
            trend: '-2%',
            trendUp: false
        },
        {
            label: 'Total Problems',
            value: this.rawStats().total_problems.toString(),
            icon: 'bi-bug',
            trend: '+18%',
            trendUp: true
        }
    ]);

    recentTasks = signal([
        { id: 1, title: 'Upgrade Production Database', priority: 'High', status: 'In Progress' },
        { id: 2, title: 'Regional Office API Integration', priority: 'Medium', status: 'Pending' },
        { id: 3, title: 'Security Audit - Branch A', priority: 'High', status: 'Completed' }
    ]);

    rawStats = signal({
        total_tasks: 0,
        active_tasks: 0,
        overdue_tasks: 0,
        total_problems: 0
    });

    filteredStats = computed(() => {
        const config = this.currentOrg()?.dashboard_metrics_config || 'tasks,active,overdue,problems';
        const allowed = config.split(',').map(s => s.trim().toLowerCase());
        return this.stats().filter(stat => {
            const label = stat.label.toLowerCase();
            if (label.includes('total tasks')) return allowed.includes('tasks');
            if (label.includes('active tasks')) return allowed.includes('active');
            if (label.includes('overdue')) return allowed.includes('overdue');
            if (label.includes('problems')) return allowed.includes('problems');
            return true;
        });
    });

    orderedWidgets = computed(() => {
        const layout = this.currentOrg()?.dashboard_layout || 'clock,stats,tasks,map';
        return layout.split(',').map(s => s.trim().toLowerCase());
    });

    getWidgetOrder(widgetName: string): number {
        const index = this.orderedWidgets().indexOf(widgetName);
        return index !== -1 ? index : 99;
    }

    ngOnInit() {
        this.timer = setInterval(() => {
            this.currentTime.set(new Date());
        }, 1000);

        this.loadBranches();
        this.loadDashboardData();

        // Reactive refresh logic
        effect(() => {
            const org = this.currentOrg();
            const interval = (org?.dashboard_refresh_rate || 30) * 1000;
            this.startRefreshTimer(interval);
        });
    }

    private startRefreshTimer(interval: number) {
        if (this.refreshTimer) clearInterval(this.refreshTimer);
        this.refreshTimer = setInterval(() => {
            console.log('Refreshing dashboard data...');
            this.loadBranches();
            this.loadDashboardData();
        }, interval);
    }

    loadBranches() {
        this.hierarchyService.getBranches().subscribe({
            next: (branches) => this.branches.set(branches),
            error: (err) => console.error('Failed to load branches', err)
        });
    }

    loadDashboardData() {
        // Load statistics
        this.hierarchyService.getDashboardStats().subscribe({
            next: (stats) => this.rawStats.set(stats),
            error: (err) => console.error('Failed to load dashboard stats', err)
        });

        // Load recent tasks
        this.hierarchyService.getRecentTasks(5).subscribe({
            next: (tasks) => this.recentTasks.set(tasks),
            error: (err) => console.error('Failed to load recent tasks', err)
        });
    }

    onTaskCreated() {
        this.loadDashboardData();
    }

    ngOnDestroy() {
        if (this.timer) clearInterval(this.timer);
        if (this.refreshTimer) clearInterval(this.refreshTimer);
    }
}
