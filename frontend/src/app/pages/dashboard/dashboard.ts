import { Component, signal, inject, OnInit, OnDestroy, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../../services/theme.service';
import { HierarchyService, Branch } from '../../services/hierarchy.service';
import { TaskCreateModal } from '../../components/task-create-modal/task-create-modal';
import { CalendarComponent } from '../../components/calendar/calendar';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, TaskCreateModal, CalendarComponent, TranslatePipe],
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
    showCustomizer = false;
    isEditMode = signal(false);

    private timer: any;
    private refreshTimer: any;

    // Widget Visibility Signals (Personal Customization)
    showClock = signal<boolean>(localStorage.getItem('dash_show_clock') !== 'false');
    showStats = signal<boolean>(localStorage.getItem('dash_show_stats') !== 'false');
    showTasks = signal<boolean>(localStorage.getItem('dash_show_tasks') !== 'false');
    showCalendar = signal<boolean>(localStorage.getItem('dash_show_calendar') !== 'false');

    // Local Widget Order (Personal Customization)
    localWidgetOrder = signal<string[]>(
        localStorage.getItem('dash_widget_order')
            ? JSON.parse(localStorage.getItem('dash_widget_order')!)
            : []
    );

    // Local Widget Sizes (Personal Customization)
    localWidgetSizes = signal<Record<string, number>>(
        localStorage.getItem('dash_widget_sizes')
            ? JSON.parse(localStorage.getItem('dash_widget_sizes')!)
            : {
                'clock': 4,
                'stats': 8,
                'tasks': 6,
                'map': 6,
                'calendar': 12
            }
    );

    getWidgetSize(widget: string): number {
        return this.localWidgetSizes()[widget] || 6;
    }

    resizeWidget(widget: string, delta: number) {
        const currentSizes = { ...this.localWidgetSizes() };
        const currentSize = currentSizes[widget] || 6;

        // Allowed spans: 4, 6, 8, 12
        const spans = [4, 6, 8, 12];
        const currentIndex = spans.indexOf(currentSize);
        let newIndex = currentIndex + delta;

        if (newIndex >= 0 && newIndex < spans.length) {
            currentSizes[widget] = spans[newIndex];
            this.localWidgetSizes.set(currentSizes);
            localStorage.setItem('dash_widget_sizes', JSON.stringify(currentSizes));
        }
    }

    toggleEditMode() {
        this.isEditMode.update(v => !v);
        if (!this.isEditMode()) {
            this.showCustomizer = false;
        }
    }

    moveWidget(widget: string, direction: 'up' | 'down') {
        const order = [...this.orderedWidgets()];
        const index = order.indexOf(widget);
        if (index === -1) return;

        const newIndex = direction === 'up' ? index - 1 : index + 1;
        if (newIndex < 0 || newIndex >= order.length) return;

        // Swap
        [order[index], order[newIndex]] = [order[newIndex], order[index]];

        this.localWidgetOrder.set(order);
        localStorage.setItem('dash_widget_order', JSON.stringify(order));
    }

    toggleWidget(widget: string) {
        if (widget === 'clock') {
            this.showClock.update(v => !v);
            localStorage.setItem('dash_show_clock', this.showClock().toString());
        } else if (widget === 'stats') {
            this.showStats.update(v => !v);
            localStorage.setItem('dash_show_stats', this.showStats().toString());
        } else if (widget === 'tasks') {
            this.showTasks.update(v => !v);
            localStorage.setItem('dash_show_tasks', this.showTasks().toString());
        } else if (widget === 'calendar') {
            this.showCalendar.update(v => !v);
            localStorage.setItem('dash_show_calendar', this.showCalendar().toString());
        }
    }

    // Analog clock rotations
    secondRotation = computed(() => this.currentTime().getSeconds() * 6);
    minuteRotation = computed(() => this.currentTime().getMinutes() * 6 + this.currentTime().getSeconds() * 0.1);
    hourRotation = computed(() => (this.currentTime().getHours() % 12) * 30 + this.currentTime().getMinutes() * 0.5);

    stats = computed(() => [
        {
            label: 'TOTAL_TASKS',
            value: this.rawStats().total_tasks.toString(),
            icon: 'bi-list-task',
            trend: '',
            trendUp: true
        },
        {
            label: 'ACTIVE_TASKS',
            value: this.rawStats().active_tasks.toString(),
            icon: 'bi-play-circle',
            trend: '',
            trendUp: true
        },
        {
            label: 'OVERDUE',
            value: this.rawStats().overdue_tasks.toString(),
            icon: 'bi-exclamation-triangle',
            trend: '',
            trendUp: false
        },
        {
            label: 'TOTAL_PROBLEMS',
            value: this.rawStats().total_problems.toString(),
            icon: 'bi-bug',
            trend: '',
            trendUp: true
        }
    ]);

    recentTasks = signal<any[]>([]);

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
        if (this.localWidgetOrder().length > 0) {
            return this.localWidgetOrder();
        }
        const layout = this.currentOrg()?.dashboard_layout || 'clock,stats,tasks,map,calendar';
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
