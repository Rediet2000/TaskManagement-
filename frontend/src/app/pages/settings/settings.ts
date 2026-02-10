import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HierarchyService, Organization } from '../../services/hierarchy.service';
import { AuthService } from '../../services/auth.service';
import { RbacService, Role as RbacRole } from '../../services/rbac.service';
import { ThemeService } from '../../services/theme.service';

@Component({
    selector: 'app-settings',
    standalone: true,
    imports: [CommonModule, FormsModule],
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
        telegramChatId: ''
    };

    branding = {
        systemPageTitle: 'Task Management System',
        themeMode: 'system'
    };

    dashboard = {
        showClock: true,
        showMap: false,
        showStats: true,
        showTasks: true
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
    success = '';
    error = '';
    userSuccess = '';
    userError = '';
    testSuccess = '';
    testError = '';

    ngOnInit() {
        // Refresh session to get enriched role info
        this.authService.getMe().subscribe();

        this.authService.currentUser.subscribe(user => {
            if (user) {
                this.currentUser.set(user);

                // Basic RBAC check: Only Super Admin or Admin can manage users
                const userRole = (user.role_name || '').toLowerCase();
                if (userRole.includes('admin') || userRole.includes('super')) {
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

    onToggleUserStatus(userId: number) {
        if (this.currentUser()?.id === userId) {
            this.userError = 'Cannot deactivate yourself';
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
        this.success = '';
        this.error = '';
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

                // SMTP
                this.smtp.host = orgAny.smtp_host || '';
                this.smtp.port = orgAny.smtp_port || 587;
                this.smtp.user = orgAny.smtp_user || '';
                this.smtp.password = orgAny.smtp_password || '';
                this.smtp.from_email = orgAny.smtp_from_email || '';

                // Password & Session
                this.passwordPolicy.minLength = orgAny.password_min_length || 8;
                this.passwordPolicy.requireSpecial = orgAny.password_require_special !== undefined ? orgAny.password_require_special : true;
                this.passwordPolicy.expiryDays = orgAny.password_expiry_days || 90;
                this.sessionConfig.timeoutMinutes = orgAny.session_timeout_minutes || 60;

                // LDAP
                this.ldap.enabled = !!orgAny.ldap_enabled;
                this.ldap.server = orgAny.ldap_server || '';
                this.ldap.baseDn = orgAny.ldap_base_dn || '';

                // Notifications
                this.notifications.telegramBotToken = orgAny.telegram_bot_token || '';
                this.notifications.telegramChatId = orgAny.telegram_chat_id || '';

                // Dashboard
                this.dashboard.showClock = orgAny.show_dashboard_clock !== undefined ? orgAny.show_dashboard_clock : true;
                this.dashboard.showMap = !!orgAny.show_dashboard_map;
                this.dashboard.showStats = orgAny.show_dashboard_stats !== undefined ? orgAny.show_dashboard_stats : true;
                this.dashboard.showTasks = orgAny.show_dashboard_tasks !== undefined ? orgAny.show_dashboard_tasks : true;

                this.themeService.updateTheme(org);
            },
            error: (err: any) => this.error = 'Failed to load organization settings'
        });
    }

    loadAllowedDomains() {
        this.hierarchyService.getAllowedDomains().subscribe({
            next: (domains: any[]) => this.allowedDomains.set(domains),
            error: (err: any) => console.error('Failed to load domains', err)
        });
    }

    onAddDomain() {
        if (!this.newDomain || !this.org()) return;
        this.hierarchyService.createAllowedDomain({
            domain: this.newDomain,
            org_id: this.org()!.id
        }).subscribe({
            next: () => {
                this.loadAllowedDomains();
                this.newDomain = '';
            },
            error: (err: any) => this.error = 'Failed to add domain'
        });
    }

    onDeleteDomain(id: number) {
        this.hierarchyService.deleteAllowedDomain(id).subscribe({
            next: () => this.loadAllowedDomains(),
            error: (err: any) => this.error = 'Failed to delete domain'
        });
    }

    loadRoles() {
        this.rbacService.getRoles().subscribe({
            next: (roles: RbacRole[]) => this.roles.set(roles),
            error: (err: any) => console.error('Failed to load roles', err)
        });
    }

    onUpdateSettings() {
        if (!this.org()) return;
        this.loading = true;
        this.success = '';
        this.error = '';

        const updateData = {
            email_domain: this.emailDomain,
            primary_color: this.primaryColor,
            secondary_color: this.secondaryColor,
            smtp_host: this.smtp.host,
            smtp_port: this.smtp.port,
            smtp_user: this.smtp.user,
            smtp_password: this.smtp.password,
            smtp_from_email: this.smtp.from_email,
            password_min_length: this.passwordPolicy.minLength,
            password_require_special: this.passwordPolicy.requireSpecial,
            password_expiry_days: this.passwordPolicy.expiryDays,
            session_timeout_minutes: this.sessionConfig.timeoutMinutes,
            ldap_enabled: this.ldap.enabled,
            ldap_server: this.ldap.server,
            ldap_base_dn: this.ldap.baseDn,
            telegram_bot_token: this.notifications.telegramBotToken,
            telegram_chat_id: this.notifications.telegramChatId,
            system_page_title: this.branding.systemPageTitle,
            theme_mode: this.branding.themeMode,
            show_dashboard_clock: this.dashboard.showClock,
            show_dashboard_map: this.dashboard.showMap,
            show_dashboard_stats: this.dashboard.showStats,
            show_dashboard_tasks: this.dashboard.showTasks
        };

        this.hierarchyService.updateOrganization(this.org()!.id, updateData).subscribe({
            next: (updatedOrg: Organization) => {
                this.themeService.updateTheme(updatedOrg);
                this.success = 'Settings updated successfully';
                this.loading = false;
            },
            error: (err: any) => {
                this.error = 'Failed to update settings';
                this.loading = false;
            }
        });
    }

    onCreateUser() {
        if (!this.newUser.email || !this.org()) return;

        // Password only required for new users
        if (!this.isEditingUser() && !this.newUser.password) {
            this.userError = 'Password is required for new users';
            return;
        }

        this.userLoading = true;
        this.userSuccess = '';
        this.userError = '';

        const userData: any = {
            full_name: this.newUser.fullName,
            email: this.newUser.email,
            org_id: this.org()!.id,
            role_id: this.newUser.roleId
        };

        if (this.newUser.password) {
            userData.password = this.newUser.password;
        }

        if (this.isEditingUser() && this.editUserId()) {
            this.authService.updateUser(this.editUserId()!, userData).subscribe({
                next: () => {
                    this.userSuccess = 'User updated successfully';
                    this.userLoading = false;
                    this.onCancelEdit();
                    this.loadUsers();
                },
                error: (err: any) => {
                    this.userError = err.error?.detail || 'Failed to update user';
                    this.userLoading = false;
                }
            });
        } else {
            this.authService.signup(userData).subscribe({
                next: () => {
                    this.userSuccess = 'User created successfully';
                    this.userLoading = false;
                    this.newUser = { fullName: '', email: '', password: '', roleId: null };
                    this.loadUsers();
                },
                error: (err: any) => {
                    this.userError = err.error?.detail || 'Failed to create user';
                    this.userLoading = false;
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
                    this.success = 'Logo uploaded successfully';
                    this.loading = false;
                },
                error: (err) => {
                    this.error = 'Failed to upload logo';
                    this.loading = false;
                }
            });
        }
    }

    onTestSmtp() {
        this.testLoading = true;
        this.testSuccess = '';
        this.testError = '';

        const testData = {
            smtp_host: this.smtp.host,
            smtp_port: this.smtp.port,
            smtp_user: this.smtp.user,
            smtp_password: this.smtp.password,
            smtp_from_email: this.smtp.from_email
        };

        this.hierarchyService.testSmtp(testData).subscribe({
            next: (res) => {
                this.testSuccess = res.message;
                this.testLoading = false;
            },
            error: (err) => {
                this.testError = err.error?.detail || 'SMTP test failed';
                this.testLoading = false;
            }
        });
    }
}
