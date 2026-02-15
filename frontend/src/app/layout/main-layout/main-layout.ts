import { Component, inject, signal, effect, computed, OnInit } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { CommonModule, DOCUMENT } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Title } from '@angular/platform-browser';
import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../services/theme.service';
import { NotificationService } from '../../services/notification.service';
import { TranslationService } from '../../services/translation.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-main-layout',
    standalone: true,
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, FormsModule, TranslatePipe],
    templateUrl: './main-layout.html',
    styleUrls: ['./main-layout.scss']
})
export class MainLayout implements OnInit {
    private authService = inject(AuthService);
    private themeService = inject(ThemeService);
    public notificationService = inject(NotificationService);
    public translationService = inject(TranslationService);
    private router = inject(Router);
    private titleService = inject(Title);
    private document = inject(DOCUMENT);

    currentLanguage = signal<string>('en');

    isSidebarCollapsed = false;
    isMobileSidebarActive = signal<boolean>(false);
    showNotifications = signal<boolean>(false);
    currentOrg = this.themeService.currentOrg;
    currentUser = this.authService.currentUser;

    ngOnInit() {
        this.notificationService.loadNotifications();
        // Poll for notifications every 60s
        setInterval(() => this.notificationService.loadNotifications(), 60000);

        // Load language preference
        const savedLang = localStorage.getItem('language') || this.currentUser()?.language || 'en';
        this.currentLanguage.set(savedLang);
    }

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
            { label: 'DASHBOARD', route: '/', icon: 'bi-grid-1x2-fill' },
            { label: 'TASKS', route: '/tasks', icon: 'bi-list-check' },
            { label: 'AGILE_BOARD', route: '/agile', icon: 'bi-kanban-fill' },
            { label: 'PROBLEM_AREAS', route: '/problems', icon: 'bi-exclamation-octagon-fill' },
            { label: 'RBAC_ORG', route: '/rbac', icon: 'bi-shield-lock-fill' },
            { label: 'ANALYTICS', route: '/analytics', icon: 'bi-bar-chart-fill' },
            { label: 'REPORTS', route: '/reports', icon: 'bi-graph-up-arrow' },
            { label: 'KNOWLEDGE_BASE', route: '/notes', icon: 'bi-journal-text' },
            { label: 'ARCHIVE', route: '/archive', icon: 'bi-archive-fill' },
            { label: 'SETTINGS', route: '/settings', icon: 'bi-gear-fill' }
        ];

        if (isAdmin) {
            // Insert Admin Dashboard after regular Dashboard
            items.splice(1, 0, { label: 'ADMIN_OVERVIEW', route: '/admin-dashboard', icon: 'bi-speedometer' });
            items.splice(2, 0, { label: 'SECURITY_LOGS', route: '/security', icon: 'bi-shield-check' });
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

    onSearch(query: string) {
        if (!query.trim()) {
            this.router.navigate(['/tasks'], { queryParams: { search: null }, queryParamsHandling: 'merge' });
        } else {
            this.router.navigate(['/tasks'], { queryParams: { search: query } });
        }
    }

    logout() {
        this.authService.logout();
        this.router.navigate(['/login']);
    }

    setLanguage(lang: string) {
        this.currentLanguage.set(lang);
        this.translationService.setLanguage(lang);

        // If user is logged in, sync with profile
        const user = this.currentUser();
        if (user) {
            this.authService.updateProfile({ ...user, language: lang }).subscribe({
                next: (updatedUser) => {
                    this.authService.currentUser.set(updatedUser);
                }
            });
        }
    }
}
