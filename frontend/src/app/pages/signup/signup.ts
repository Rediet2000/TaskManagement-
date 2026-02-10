import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { Organization } from '../../services/hierarchy.service';
import { environment } from '../../../environments/environment';

@Component({
    selector: 'app-signup',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterLink],
    templateUrl: './signup.html',
    styleUrls: ['./signup.scss']
})
export class SignUp implements OnInit {
    email = '';
    password = '';
    fullName = '';
    orgId: number | null = null;
    organizations = signal<Organization[]>([]);
    error = '';
    loading = false;

    private authService = inject(AuthService);
    private http = inject(HttpClient);
    private router = inject(Router);

    ngOnInit() {
        this.http.get<Organization[]>(`${environment.apiUrl}/hierarchy/organizations`).subscribe({
            next: (orgs) => this.organizations.set(orgs),
            error: (err) => console.error('Failed to load organizations', err)
        });
    }

    onSubmit() {
        this.loading = true;
        this.error = '';

        if (!this.orgId) {
            this.error = 'Please select an organization';
            this.loading = false;
            return;
        }

        const userData = {
            email: this.email,
            password: this.password,
            full_name: this.fullName,
            org_id: Number(this.orgId)
        };

        this.authService.signup(userData).subscribe({
            next: () => {
                this.router.navigate(['/login'], { queryParams: { signedUp: true } });
            },
            error: (err: any) => {
                this.error = err.error?.detail || 'Registration failed';
                this.loading = false;
            }
        });
    }
}
