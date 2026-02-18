import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-register-company',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterLink, TranslatePipe],
    templateUrl: './register-company.html',
    styleUrls: ['./signup.scss'] // Reuse signup styles
})
export class RegisterCompany {
    orgName = '';
    adminEmail = '';
    adminPassword = '';
    adminFullName = '';

    error = '';
    loading = false;

    private authService = inject(AuthService);
    private router = inject(Router);

    onSubmit() {
        this.loading = true;
        this.error = '';

        const data = {
            org_name: this.orgName,
            admin_email: this.adminEmail,
            admin_password: this.adminPassword,
            admin_full_name: this.adminFullName
        };

        this.authService.registerCompany(data).subscribe({
            next: () => {
                // Auto login successful, redirect to dashboard or onboarding
                this.router.navigate(['/']);
            },
            error: (err: any) => {
                this.error = err.error?.detail || 'Registration failed';
                this.loading = false;
            }
        });
    }
}
