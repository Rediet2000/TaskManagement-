import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-reset-password',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule, TranslatePipe],
    template: `
        <div class="auth-container">
            <div class="auth-card glass-card animate-fade-in">
                <div class="auth-header">
                    <img src="assets/logo.png" alt="Logo" class="auth-logo" onerror="this.src='https://placehold.co/120x40/1e293b/ffffff?text=Task+Mgmt'">
                    <h1>{{ 'SET_NEW_PASSWORD' | translate }}</h1>
                    <p class="text-muted">{{ 'NEW_PASSWORD' | translate }}</p>
                </div>

                <form (ngSubmit)="onSubmit()" #resetForm="ngForm">
                    <div class="form-group animate-slide-up" style="animation-delay: 0.1s">
                        <label for="password">{{ 'NEW_PASSWORD' | translate }}</label>
                        <div class="input-wrapper">
                            <i class="bi bi-lock"></i>
                            <input 
                                type="password" 
                                id="password" 
                                name="password" 
                                [(ngModel)]="newPassword" 
                                required 
                                minlength="8"
                                placeholder="••••••••"
                            >
                        </div>
                    </div>

                    <div class="form-group animate-slide-up" style="animation-delay: 0.15s">
                        <label for="confirm">{{ 'CONFIRM_PASSWORD' | translate }}</label>
                        <div class="input-wrapper">
                            <i class="bi bi-shield-check"></i>
                            <input 
                                type="password" 
                                id="confirm" 
                                name="confirm" 
                                [(ngModel)]="confirmPassword" 
                                required
                                placeholder="••••••••"
                            >
                        </div>
                    </div>

                    <div *ngIf="error" class="alert alert-error animate-shake">
                        <i class="bi bi-exclamation-circle"></i>
                        {{ error }}
                    </div>

                    <div *ngIf="success" class="alert alert-success">
                        <i class="bi bi-check-circle"></i>
                        {{ success }}
                    </div>

                    <button 
                        type="submit" 
                        class="btn-primary animate-slide-up" 
                        style="animation-delay: 0.2s"
                        [disabled]="loading() || !resetForm.valid || newPassword !== confirmPassword || success"
                    >
                        <span *ngIf="!loading()">{{ 'UPDATE_PASSWORD' | translate }}</span>
                        <span *ngIf="loading()" class="loader small"></span>
                    </button>

                    <div class="auth-footer animate-slide-up" style="animation-delay: 0.3s">
                        <p><a routerLink="/login">{{ 'BACK_TO_LOGIN' | translate }}</a></p>
                    </div>
                </form>
            </div>
        </div>
    `,
    styles: [`
        /* Re-using same auth styles as forgot-password for consistency */
        .auth-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at top right, rgba(37, 99, 235, 0.1), transparent),
                        radial-gradient(circle at bottom left, rgba(56, 189, 248, 0.1), transparent);
            padding: 1.5rem;
        }

        .auth-card {
            width: 100%;
            max-width: 440px;
            padding: 2.5rem;
            border-radius: 1.5rem;
        }

        .auth-header {
            text-align: center;
            margin-bottom: 2.5rem;

            .auth-logo {
                height: 48px;
                margin-bottom: 1.5rem;
            }

            h1 {
                font-size: 1.75rem;
                font-weight: 700;
                color: #fff;
                margin-bottom: 0.5rem;
            }
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;

            label {
                font-size: 0.875rem;
                font-weight: 500;
                color: var(--text-muted);
            }
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;

            i {
                position: absolute;
                left: 1rem;
                color: var(--text-muted);
                font-size: 1.1rem;
            }

            input {
                width: 100%;
                padding: 0.875rem 1rem 0.875rem 2.75rem;
                background: rgba(15, 23, 42, 0.4);
                border: 1px solid var(--glass-border);
                border-radius: 0.75rem;
                color: #fff;
                font-size: 1rem;
                transition: all 0.2s ease;

                &:focus {
                    border-color: var(--primary);
                    outline: none;
                    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
                    background: rgba(15, 23, 42, 0.6);
                }
            }
        }

        .btn-primary {
            width: 100%;
            padding: 0.875rem;
            font-size: 1rem;
            font-weight: 600;
            margin-top: 1rem;
        }

        .auth-footer {
            text-align: center;
            margin-top: 1rem;
            font-size: 0.875rem;
            color: var(--text-muted);

            a {
                color: var(--primary);
                text-decoration: none;
                font-weight: 600;
                &:hover { text-decoration: underline; }
            }
        }

        .alert {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem;
            border-radius: 0.75rem;
            font-size: 0.875rem;

            &.alert-error {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.2);
                color: #f87171;
            }

            &.alert-success {
                background: rgba(34, 197, 94, 0.1);
                border: 1px solid rgba(34, 197, 94, 0.2);
                color: #4ade80;
            }
        }
    `]
})
export class ResetPassword implements OnInit {
    private authService = inject(AuthService);
    private route = inject(ActivatedRoute);
    private router = inject(Router);

    token = '';
    newPassword = '';
    confirmPassword = '';
    loading = signal(false);
    error = '';
    success = '';

    ngOnInit() {
        this.token = this.route.snapshot.queryParamMap.get('token') || '';
        if (!this.token) {
            this.error = 'Invalid or missing reset token. Please request a new one.';
        }
    }

    onSubmit() {
        if (this.newPassword !== this.confirmPassword) {
            this.error = 'Passwords do not match';
            return;
        }

        this.loading.set(true);
        this.error = '';
        this.success = '';

        this.authService.confirmPasswordReset({
            token: this.token,
            new_password: this.newPassword
        }).subscribe({
            next: (res) => {
                this.success = res.message + '. Redirecting to login...';
                this.loading.set(false);
                setTimeout(() => this.router.navigate(['/login']), 3000);
            },
            error: (err) => {
                this.error = err.error?.detail || 'Failed to update password';
                this.loading.set(false);
            }
        });
    }
}
