import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
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

    isSidebarCollapsed = false;
    currentOrg = this.themeService.currentOrg;
    currentUser = this.authService.currentUser;

    navItems = [
        { label: 'Dashboard', route: '/', icon: 'bi-grid-1x2-fill' },
        { label: 'Tasks', route: '/tasks', icon: 'bi-list-check' },
        { label: 'Problem Areas', route: '/problems', icon: 'bi-exclamation-octagon-fill' },
        { label: 'RBAC & Org', route: '/rbac', icon: 'bi-shield-lock-fill' },
        { label: 'Analytics', route: '/analytics', icon: 'bi-bar-chart-fill' },
        { label: 'Settings', route: '/settings', icon: 'bi-gear-fill' }
    ];

    toggleSidebar() {
        this.isSidebarCollapsed = !this.isSidebarCollapsed;
    }

    logout() {
        this.authService.logout();
        this.router.navigate(['/login']);
    }
}
