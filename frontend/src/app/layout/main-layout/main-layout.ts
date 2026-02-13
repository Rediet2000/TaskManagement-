import { Component, inject, signal, effect, computed } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { CommonModule, DOCUMENT } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../services/theme.service';

@Component({
    selector: 'app-main-layout',
    standalone: true,
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
    templateUrl: './main-layout.html',
    styleUrls: ['./main-layout.scss']
})
export class MainLayout {
    private authService = inject(AuthService);
    private themeService = inject(ThemeService);
    private router = inject(Router);
    private titleService = inject(Title);
    private document = inject(DOCUMENT);

    isSidebarCollapsed = false;
    isMobileSidebarActive = signal<boolean>(false);
    currentOrg = this.themeService.currentOrg;
    currentUser = this.authService.currentUser;

    constructor() {
        effect(() => {
            const org = this.currentOrg();
            // Update Title
            if (org?.name) {
                this.titleService.setTitle(org.name);
            } else {
                this.titleService.setTitle('Task Management System');
            }

            // Update Favicon
            const link = this.document.querySelector("link[rel~='icon']") as HTMLLinkElement;
            if (link) {
                link.href = org?.logo_url || 'favicon.ico';
            }
        });
    }

    navItems = computed(() => {
        const user = this.currentUser();
        const role = (user?.role_name || '').toLowerCase();
        const isAdmin = role.includes('admin') || role.includes('super');

        const items = [
            { label: 'Dashboard', route: '/', icon: 'bi-grid-1x2-fill' },
            { label: 'Tasks', route: '/tasks', icon: 'bi-list-check' },
            { label: 'Agile Board', route: '/agile', icon: 'bi-kanban-fill' },
            { label: 'Problem Areas', route: '/problems', icon: 'bi-exclamation-octagon-fill' },
            { label: 'RBAC & Org', route: '/rbac', icon: 'bi-shield-lock-fill' },
            { label: 'Analytics', route: '/analytics', icon: 'bi-bar-chart-fill' },
            { label: 'Reports', route: '/reports', icon: 'bi-graph-up-arrow' },
            { label: 'Knowledge Base', route: '/notes', icon: 'bi-journal-text' },
            { label: 'Settings', route: '/settings', icon: 'bi-gear-fill' }
        ];

        if (isAdmin) {
            // Insert Admin Dashboard after regular Dashboard
            items.splice(1, 0, { label: 'Admin Overview', route: '/admin-dashboard', icon: 'bi-speedometer' });
        }

        return items;
    });

    toggleSidebar() {
        if (window.innerWidth <= 1024) {
            this.isMobileSidebarActive.update(v => !v);
        } else {
            this.isSidebarCollapsed = !this.isSidebarCollapsed;
        }
    }

    logout() {
        this.authService.logout();
        this.router.navigate(['/login']);
    }
}
