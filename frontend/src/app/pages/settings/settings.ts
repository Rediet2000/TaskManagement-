import { Component, inject, signal, OnInit, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HierarchyService, Organization } from '../../services/hierarchy.service';
import { AuthService } from '../../services/auth.service';
import { RbacService, Role as RbacRole } from '../../services/rbac.service';
import { ThemeService } from '../../services/theme.service';

import { TranslationService } from '../../services/translation.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-settings',
    standalone: true,
    imports: [CommonModule, FormsModule, TranslatePipe],
    templateUrl: './settings.html',
    styleUrls: ['./settings.scss']
})
export class Settings implements OnInit {
    private hierarchyService = inject(HierarchyService);
    private authService = inject(AuthService);
    private rbacService = inject(RbacService);
    private themeService = inject(ThemeService);

    activeTab = signal<string>('user-access');
    org = this.themeService.currentOrg;
    roles = signal<RbacRole[]>([]);
    allowedDomains = signal<any[]>([]);
    users = signal<any[]>([]);

    currentUser = signal<any>(null);
    canManageUsers = signal<boolean>(false);
    isEditingUser = signal<boolean>(false);
    editUserId = signal<number | null>(null);
    togglingUserId = signal<number | null>(null);

    // Configuration Objects
    emailDomain = '';
    primaryColor = '#2563eb';
    secondaryColor = '#64748b';
    newDomain = '';

    smtp = {
        host: '',
        port: 587,
        user: '',
        password: '',
        from_email: ''
    };

    passwordPolicy = {
        minLength: 8,
        requireSpecial: true,
        expiryDays: 90
    };

    sessionConfig = {
        timeoutMinutes: 60
    };

    ldap = {
        enabled: false,
        server: '',
        baseDn: ''
    };

    notifications = {
        telegramBotToken: '',
        telegramChatId: '',
        telegramEnabled: false,
        emailNotificationsEnabled: true
    };

    branding = {
        systemPageTitle: 'Task Management System',
        themeMode: 'system'
    };

    companyProfile = {
        industry: '',
        address: '',
        timezone: 'UTC',
        default_language: 'en',
        contact_phone: '',
        contact_email: ''
    };

    dashboard = {
        showClock: true,
        showMap: false,
        showStats: true,
        showTasks: true,
        layout: 'clock,stats,tasks,map',
        refreshRate: 30,
        clockType: 'analog',
        metricsConfig: 'tasks,active,overdue,problems',
        compactMode: false
    };

    newUser = {
        fullName: '',
        email: '',
        password: '',
        roleId: null as number | null
    };

    // UI States
    loading = false;
    userLoading = false;
    testLoading = false;
    success = signal('');
    error = signal('');
    userSuccess = signal('');
    userError = signal('');
    testSuccess = signal('');
    testError = signal('');

    private autoDismiss(type: 'global' | 'user' | 'test' = 'global') {
        setTimeout(() => {
            if (type === 'global') {
                this.success.set('');
                this.error.set('');
            } else if (type === 'user') {
                this.userSuccess.set('');
                this.userError.set('');
            } else if (type === 'test') {
                this.testSuccess.set('');
                this.testError.set('');
            }
        }, 10000);
    }

    constructor() {
        effect(() => {
            const user = this.authService.currentUser();
            if (user) {
                this.currentUser.set(user);

                // Basic RBAC check: Only Super Admin or those with user:invite permission can manage users
                if (this.authService.hasPermission('user:invite')) {
                    this.canManageUsers.set(true);
                } else {
                    this.canManageUsers.set(false);
                }

                if (user.org_id) {
                    this.loadOrg(user.org_id);
                    this.loadRoles();
                    this.loadAllowedDomains();
                    this.loadUsers();
                }
            }
        });
    }

    ngOnInit() {
        // Refresh session to get enriched role info
        this.authService.getMe().subscribe();
    }

    onEditUser(user: any) {
        this.isEditingUser.set(true);
        this.editUserId.set(user.id);
        this.newUser = {
            fullName: user.full_name,
            email: user.email,
            password: '', // Keep empty unless updating
            roleId: user.role_id
        };
        // Scroll to form
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    onCancelEdit() {
        this.isEditingUser.set(false);
        this.editUserId.set(null);
        this.newUser = { fullName: '', email: '', password: '', roleId: null };
    }

    loadUsers() {
        this.authService.getUsers().subscribe({
            next: (data) => this.users.set(data),
            error: (err) => console.error('Failed to load users', err)
        });
    }

    loadRoles() {
        this.rbacService.getRoles().subscribe({
            next: (data) => this.roles.set(data),
            error: (err) => console.error('Failed to load roles', err)
        });
    }

    loadAllowedDomains() {
        // hierarchyService.getAllowedDomains(orgId) implementation needed
        // For now, assuming it exists or using a placeholder if service is missing it
        if (this.org()) {
            this.hierarchyService.getAllowedDomains().subscribe({
                next: (data) => this.allowedDomains.set(data),
                error: (err) => console.error('Failed to load allowed domains', err)
            });
        }
    }

    onAddDomain() {
        const domain = this.newDomain.trim();
        if (!domain || !this.org()) return;

        const domainData = {
            domain: domain,
            org_id: this.org()!.id
        };

        this.loading = true;
        this.hierarchyService.createAllowedDomain(domainData).subscribe({
            next: () => {
                this.success.set('Domain added successfully');
                this.loading = false;
                this.newDomain = '';
                this.loadAllowedDomains();
                this.autoDismiss('global');
            },
            error: (err) => {
                this.error.set(err.error?.detail || 'Failed to add domain');
                this.loading = false;
                this.autoDismiss('global');
            }
        });
    }

    onDeleteDomain(id: number) {
        if (!confirm('Are you sure you want to remove this domain?')) return;

        this.loading = true;
        this.hierarchyService.deleteAllowedDomain(id).subscribe({
            next: () => {
                this.success.set('Domain removed successfully');
                this.loading = false;
                this.loadAllowedDomains();
                this.autoDismiss('global');
            },
            error: (err) => {
                this.error.set(err.error?.detail || 'Failed to remove domain');
                this.loading = false;
                this.autoDismiss('global');
            }
        });
    }

    onToggleUserStatus(userId: number) {
        if (this.currentUser()?.id === userId) {
            this.userError.set('Cannot deactivate yourself');
            return;
        }

        this.togglingUserId.set(userId);
        this.authService.toggleUserStatus(userId).subscribe({
            next: () => {
                this.loadUsers();
                this.togglingUserId.set(null);
            },
            error: (err) => {
                this.userError = err.error?.detail || 'Failed to toggle user status';
                this.togglingUserId.set(null);
            }
        });
    }

    setTab(tab: string) {
        this.activeTab.set(tab);
        this.success.set('');
        this.error.set('');
    }

    loadOrg(id: number) {
        this.hierarchyService.getOrganization(id).subscribe({
            next: (org: Organization) => {
                const orgAny = org as any;

                // Branding
                this.emailDomain = org.email_domain || '';
                this.primaryColor = org.primary_color || '#2563eb';
                this.secondaryColor = org.secondary_color || '#64748b';
                this.branding.systemPageTitle = orgAny.system_page_title || 'Task Management System';
                this.branding.themeMode = orgAny.theme_mode || 'system';

                // Company Profile
                this.companyProfile.industry = orgAny.industry || '';
                this.companyProfile.address = orgAny.address || '';
                this.companyProfile.timezone = orgAny.timezone || 'UTC';
                this.companyProfile.default_language = orgAny.default_language || 'en';
                this.companyProfile.contact_phone = orgAny.contact_phone || '';
                this.companyProfile.contact_email = orgAny.contact_email || '';

                // SMTP
                this.smtp.host = orgAny.smtp_host || '';
                this.smtp.port = orgAny.smtp_port || 587;
                this.smtp.user = orgAny.smtp_user || '';
                this.smtp.password = orgAny.smtp_password || '';
                this.smtp.from_email = orgAny.smtp_from_email || '';

                // Advanced Dashboard
                this.dashboard.showClock = orgAny.show_dashboard_clock ?? true;
                this.dashboard.showMap = orgAny.show_dashboard_map ?? false;
                this.dashboard.showStats = orgAny.show_dashboard_stats ?? true;
                this.dashboard.showTasks = orgAny.show_dashboard_tasks ?? true;
                this.dashboard.layout = orgAny.dashboard_layout || 'clock,stats,tasks,map';
                this.dashboard.refreshRate = orgAny.dashboard_refresh_rate || 30;
                this.dashboard.clockType = orgAny.dashboard_clock_type || 'analog';
                this.dashboard.metricsConfig = orgAny.dashboard_metrics_config || 'tasks,active,overdue,problems';
                this.dashboard.compactMode = orgAny.dashboard_compact_mode ?? false;

                // Notifications
                this.notifications.telegramBotToken = orgAny.telegram_bot_token || '';
                this.notifications.telegramChatId = orgAny.telegram_chat_id || '';
                this.notifications.telegramEnabled = orgAny.telegram_enabled ?? false;
                this.notifications.emailNotificationsEnabled = orgAny.email_notifications_enabled ?? true;
            },
            error: (err) => console.error('Failed to load org settings', err)
        });
    }

    onUpdateSettings() {
        if (!this.org()) return;
        this.loading = true;
        this.success.set('');
        this.error.set('');

        const updateData = {
            email_domain: this.emailDomain,
            primary_color: this.primaryColor,
            secondary_color: this.secondaryColor,
            smtp_host: this.smtp.host,
            smtp_port: this.smtp.port,
            smtp_user: this.smtp.user,
            smtp_password: this.smtp.password,
            smtp_from_email: this.smtp.from_email,

            industry: this.companyProfile.industry,
            address: this.companyProfile.address,
            timezone: this.companyProfile.timezone,
            default_language: this.companyProfile.default_language,
            contact_phone: this.companyProfile.contact_phone,
            contact_email: this.companyProfile.contact_email,

            password_min_length: this.passwordPolicy.minLength,
            password_require_special: this.passwordPolicy.requireSpecial,
            password_expiry_days: this.passwordPolicy.expiryDays,
            session_timeout_minutes: this.sessionConfig.timeoutMinutes,
            ldap_enabled: this.ldap.enabled,
            ldap_server: this.ldap.server,
            ldap_base_dn: this.ldap.baseDn,
            telegram_bot_token: this.notifications.telegramBotToken,
            telegram_chat_id: this.notifications.telegramChatId,
            telegram_enabled: this.notifications.telegramEnabled,
            email_notifications_enabled: this.notifications.emailNotificationsEnabled,
            system_page_title: this.branding.systemPageTitle,
            theme_mode: this.branding.themeMode,
            show_dashboard_clock: this.dashboard.showClock,
            show_dashboard_map: this.dashboard.showMap,
            show_dashboard_stats: this.dashboard.showStats,
            show_dashboard_tasks: this.dashboard.showTasks,
            dashboard_layout: this.dashboard.layout,
            dashboard_refresh_rate: this.dashboard.refreshRate,
            dashboard_clock_type: this.dashboard.clockType,
            dashboard_metrics_config: this.dashboard.metricsConfig,
            dashboard_compact_mode: this.dashboard.compactMode
        };

        this.hierarchyService.updateOrganization(this.org()!.id, updateData).subscribe({
            next: (updatedOrg: Organization) => {
                this.themeService.updateTheme(updatedOrg);
                this.success.set('Settings updated successfully');
                this.loading = false;
                this.autoDismiss('global');
            },
            error: (err: any) => {
                this.error.set('Failed to update settings');
                this.loading = false;
                this.autoDismiss('global');
            }
        });
    }

    onCreateUser() {
        if (!this.newUser.email || !this.org()) return;

        // Password only required when editing if user wants to change it
        // For new users, we use invite flow (no password needed from admin)

        this.userLoading = true;
        this.userSuccess.set('');
        this.userError.set('');

        const userData: any = {
            full_name: this.newUser.fullName,
            email: this.newUser.email,
            org_id: this.org()!.id,
            role_id: this.newUser.roleId
        };

        if (this.isEditingUser()) {
            if (this.newUser.password) {
                userData.password = this.newUser.password;
            }
            if (this.editUserId()) {
                this.authService.updateUser(this.editUserId()!, userData).subscribe({
                    next: () => {
                        this.userSuccess.set('User updated successfully');
                        this.userLoading = false;
                        this.onCancelEdit();
                        this.loadUsers();
                        this.autoDismiss('user');
                    },
                    error: (err: any) => {
                        this.userError.set(err.error?.detail || 'Failed to update user');
                        this.userLoading = false;
                        this.autoDismiss('user');
                    }
                });
            }
        } else {
            // Invite new user
            this.authService.inviteUser(userData).subscribe({
                next: () => {
                    this.userSuccess.set('User invited successfully. They will receive an email with login details.');
                    this.userLoading = false;
                    this.newUser = { fullName: '', email: '', password: '', roleId: null };
                    this.loadUsers();
                    this.autoDismiss('user');
                },
                error: (err: any) => {
                    this.userError.set(err.error?.detail || 'Failed to invite user');
                    this.userLoading = false;
                    this.autoDismiss('user');
                }
            });
        }
    }

    onFileSelected(event: any) {
        const file = event.target.files[0];
        if (file && this.org()) {
            this.loading = true;
            this.hierarchyService.uploadLogo(this.org()!.id, file).subscribe({
                next: (updatedOrg) => {
                    this.themeService.updateTheme(updatedOrg);
                    this.success.set('Logo uploaded successfully');
                    this.loading = false;
                    this.autoDismiss('global');
                },
                error: (err) => {
                    this.error.set('Failed to upload logo');
                    this.loading = false;
                    this.autoDismiss('global');
                }
            });
        }
    }

    onTestSmtp() {
        this.testLoading = true;
        this.testSuccess.set('');
        this.testError.set('');

        const testData = {
            smtp_host: this.smtp.host,
            smtp_port: this.smtp.port,
            smtp_user: this.smtp.user,
            smtp_password: this.smtp.password,
            smtp_from_email: this.smtp.from_email
        };

        this.hierarchyService.testSmtp(testData).subscribe({
            next: (res) => {
                this.testSuccess.set(res.message);
                this.testLoading = false;
                this.autoDismiss('test');
            },
            error: (err) => {
                this.testError.set(err.error?.detail || 'SMTP test failed');
                this.testLoading = false;
                this.autoDismiss('test');
            }
        });
    }

    onTestTelegram() {
        if (!this.notifications.telegramBotToken || !this.notifications.telegramChatId) {
            this.testError.set('Bot Token and Chat ID are required for testing.');
            this.autoDismiss('test');
            return;
        }

        this.testLoading = true;
        this.testSuccess.set('');
        this.testError.set('');

        this.hierarchyService.testTelegram(
            this.notifications.telegramBotToken,
            this.notifications.telegramChatId
        ).subscribe({
            next: (res) => {
                this.testSuccess.set(res.message);
                this.testLoading = false;
                this.autoDismiss('test');
            },
            error: (err) => {
                this.testError.set(err.error?.detail || 'Telegram test failed');
                this.testLoading = false;
                this.autoDismiss('test');
            }
        });
    }
}
