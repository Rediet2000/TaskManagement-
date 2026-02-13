import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { TaskService } from '../../services/task.service';

@Component({
    selector: 'app-profile',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './profile.html',
    styleUrls: ['./profile.scss']
})
export class Profile implements OnInit {
    private authService = inject(AuthService);
    private taskService = inject(TaskService);

    user = signal<any>(null);
    stats = signal({
        open: 0,
        completed: 0,
        overdue: 0
    });

    activeTab = signal('personal'); // personal, preferences, security, notifications, activity

    loading = signal(false);
    success = signal('');
    error = signal('');

    // Password Change
    passwordData = {
        old_password: '',
        new_password: '',
        confirm_password: ''
    };

    ngOnInit() {
        this.loadProfile();
        this.loadStats();
    }

    loadProfile() {
        const user = this.authService.currentUser();
        if (user) {
            this.prepareUser(user);
        }
    }

    private prepareUser(user: any) {
        const userCopy = JSON.parse(JSON.stringify(user));

        // Ensure email_notifications and in_app_notifications are objects
        try {
            if (typeof userCopy.email_notifications === 'string') {
                userCopy.email_notifications = JSON.parse(userCopy.email_notifications);
            }
        } catch (e) { userCopy.email_notifications = {}; }

        try {
            if (typeof userCopy.in_app_notifications === 'string') {
                userCopy.in_app_notifications = JSON.parse(userCopy.in_app_notifications);
            }
        } catch (e) { userCopy.in_app_notifications = {}; }

        // Final fallback to empty objects
        userCopy.email_notifications = userCopy.email_notifications || {};
        userCopy.in_app_notifications = userCopy.in_app_notifications || {};

        this.user.set(userCopy);
    }

    loadStats() {
        // Mocking stats for now, later connect to actual task reporting
        this.stats.set({
            open: 12,
            completed: 45,
            overdue: 2
        });
    }

    setTab(tab: string) {
        this.activeTab.set(tab);
        this.success.set('');
        this.error.set('');
    }

    saveProfile() {
        this.loading.set(true);
        this.authService.updateProfile(this.user()).subscribe({
            next: (updatedUser) => {
                this.authService.currentUser.set(updatedUser);
                this.success.set('Operational profile synchronized successfully.');
                this.loading.set(false);
                setTimeout(() => this.success.set(''), 3000);
            },
            error: (err) => {
                this.error.set(err.error?.detail || 'Profile synchronization failed.');
                this.loading.set(false);
            }
        });
    }

    changePassword() {
        if (this.passwordData.new_password !== this.passwordData.confirm_password) {
            this.error.set('Password confirmation mismatch.');
            return;
        }

        this.loading.set(true);
        // Only sending the fields the backend expects
        const payload = {
            old_password: this.passwordData.old_password,
            new_password: this.passwordData.new_password
        };

        this.authService.changePassword(payload).subscribe({
            next: () => {
                this.success.set('Security credentials updated.');
                this.passwordData = { old_password: '', new_password: '', confirm_password: '' };
                this.loading.set(false);
                setTimeout(() => this.success.set(''), 3000);
            },
            error: (err) => {
                this.error.set(err.error?.detail || 'Security update failed.');
                this.loading.set(false);
            }
        });
    }

    onPhotoUpload(event: any) {
        const file = event.target.files[0];
        if (file) {
            this.loading.set(true);
            this.authService.uploadProfilePhoto(file).subscribe({
                next: (res) => {
                    this.user.update(u => ({ ...u, profile_photo_url: res.profile_photo_url }));
                    // Update the global state immediately
                    const currentUser = this.authService.currentUser();
                    if (currentUser) {
                        const updated = { ...currentUser, profile_photo_url: res.profile_photo_url };
                        this.authService.currentUser.set(updated);
                        localStorage.setItem('currentUser', JSON.stringify(updated));
                    }
                    this.success.set('Strategic avatar updated.');
                    this.loading.set(false);
                    setTimeout(() => this.success.set(''), 3000);
                },
                error: (err) => {
                    this.error.set(err.error?.detail || 'Avatar deployment failed.');
                    this.loading.set(false);
                }
            });
        }
    }
}
