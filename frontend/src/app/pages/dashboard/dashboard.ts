import { Component, signal, inject, OnInit, OnDestroy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../../services/theme.service';
import { HierarchyService, Branch } from '../../services/hierarchy.service';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './dashboard.html',
    styleUrls: ['./dashboard.scss']
})
export class Dashboard implements OnInit, OnDestroy {
    private themeService = inject(ThemeService);
    private hierarchyService = inject(HierarchyService);

    currentOrg = this.themeService.currentOrg;

    currentTime = signal(new Date());
    branches = signal<Branch[]>([]);
    private timer: any;

    // Analog clock rotations
    secondRotation = computed(() => this.currentTime().getSeconds() * 6);
    minuteRotation = computed(() => this.currentTime().getMinutes() * 6 + this.currentTime().getSeconds() * 0.1);
    hourRotation = computed(() => (this.currentTime().getHours() % 12) * 30 + this.currentTime().getMinutes() * 0.5);

    stats = signal([
        { label: 'Total Tasks', value: '128', icon: 'bi-list-task', trend: '+12%', trendUp: true },
        { label: 'Active Tasks', value: '42', icon: 'bi-play-circle', trend: '+5%', trendUp: true },
        { label: 'Overdue', value: '8', icon: 'bi-exclamation-triangle', trend: '-2%', trendUp: false },
        { label: 'Total Problems', value: '24', icon: 'bi-bug', trend: '+18%', trendUp: true }
    ]);

    recentTasks = signal([
        { id: 1, title: 'Upgrade Production Database', priority: 'High', status: 'In Progress' },
        { id: 2, title: 'Regional Office API Integration', priority: 'Medium', status: 'Pending' },
        { id: 3, title: 'Security Audit - Branch A', priority: 'High', status: 'Completed' }
    ]);

    ngOnInit() {
        this.timer = setInterval(() => {
            this.currentTime.set(new Date());
        }, 1000);

        this.loadBranches();
    }

    loadBranches() {
        this.hierarchyService.getBranches().subscribe({
            next: (branches) => this.branches.set(branches),
            error: (err) => console.error('Failed to load branches', err)
        });
    }

    ngOnDestroy() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }
}
