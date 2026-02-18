import { Injectable, signal, effect, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Organization, HierarchyService } from './hierarchy.service';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class ThemeService {
    private hierarchyService = inject(HierarchyService);
    private authService = inject(AuthService);

    currentOrg = signal<Organization | null>(null);
    private mediaQueryListener: any = null;

    constructor() {
        effect(() => {
            const user = this.authService.currentUser();
            if (user && user.org_id) {
                this.loadTheme(user.org_id);
            } else {
                this.currentOrg.set(null);
                this.resetTheme();
            }
        });

        effect(() => {
            const org = this.currentOrg();
            if (org) {
                this.applyTheme(org);
            }
        });
    }

    private loadTheme(orgId: number) {
        this.hierarchyService.getOrganization(orgId).subscribe({
            next: (org) => {
                org.logo_url = this.getFullLogoUrl(org.logo_url);
                this.currentOrg.set(org);
            },
            error: (err) => console.error('Failed to load theme', err)
        });
    }

    private getFullLogoUrl(logoUrl: string | undefined): string | undefined {
        if (!logoUrl) return undefined;
        if (logoUrl.startsWith('http')) return logoUrl;

        // Base API URL is http://localhost:8000/api/v1
        // Base server URL is http://localhost:8000
        const baseUrl = environment.apiUrl.split('/api/')[0];
        return `${baseUrl}${logoUrl}`;
    }

    private applyTheme(org: Organization) {
        const root = document.documentElement;

        if (org.primary_color) {
            root.style.setProperty('--primary', org.primary_color);
            // Derive hover color (simple darkening)
            root.style.setProperty('--primary-hover', this.adjustColor(org.primary_color, -10));
        }

        if (org.secondary_color) {
            root.style.setProperty('--accent', org.secondary_color);
        }

        if (org.border_radius) {
            root.style.setProperty('--glass-radius', org.border_radius);
        }

        if (org.font_family) {
            root.style.setProperty('--font-family', org.font_family);
        }

        if (org.font_size_base) {
            root.style.setProperty('--font-size-base', org.font_size_base);
        }

        this.setThemeMode(org.theme_mode || 'system');
    }

    private setThemeMode(mode: string) {
        const root = document.documentElement;

        // Clean up previous listener
        if (this.mediaQueryListener) {
            window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.mediaQueryListener);
            this.mediaQueryListener = null;
        }

        if (mode === 'system') {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            const updateTheme = (e: MediaQueryListEvent | MediaQueryList) => {
                root.setAttribute('data-theme', e.matches ? 'dark' : 'light');
                console.log(`--- System Theme Changed: ${e.matches ? 'dark' : 'light'} ---`);
            };

            updateTheme(mediaQuery);
            this.mediaQueryListener = (e: MediaQueryListEvent) => updateTheme(e);
            mediaQuery.addEventListener('change', this.mediaQueryListener);
        } else {
            root.setAttribute('data-theme', mode);
        }
        console.log(`--- Theme Mode Applied: ${mode} ---`);
    }

    private resetTheme() {
        const root = document.documentElement;
        root.style.removeProperty('--primary');
        root.style.removeProperty('--primary-hover');
        root.style.removeProperty('--accent');
        root.removeAttribute('data-theme');

        if (this.mediaQueryListener) {
            window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.mediaQueryListener);
            this.mediaQueryListener = null;
        }
    }

    private adjustColor(hex: string, percent: number) {
        const num = parseInt(hex.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return '#' + (0x1000000 + (R < 255 ? R < 0 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 0 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 0 ? 0 : B : 255)).toString(16).slice(1);
    }

    updateTheme(org: Organization) {
        org.logo_url = this.getFullLogoUrl(org.logo_url);
        this.currentOrg.set(org);
    }
}
