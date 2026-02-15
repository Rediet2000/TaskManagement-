import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslatePipe } from '../../pipes/translate.pipe';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { Organization } from '../../services/hierarchy.service';
import { environment } from '../../../environments/environment';

@Component({
    selector: 'app-signup',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterLink, TranslatePipe],
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

    invitationToken: string | null = null;
    isInvited = signal<boolean>(false);
    invitedOrgName = signal<string>('');
    roleId: number | null = null;

    private authService = inject(AuthService);
    private http = inject(HttpClient);
    private router = inject(Router);
    private route = inject(ActivatedRoute);

    ngOnInit() {
        this.invitationToken = this.route.snapshot.queryParams['invitation_token'];

        if (this.invitationToken) {
            this.authService.getInvitation(this.invitationToken).subscribe({
                next: (inv) => {
                    this.email = inv.email;
                    this.orgId = inv.org_id;
                    this.invitedOrgName.set(inv.org_name);
                    this.isInvited.set(true);
                    this.roleId = inv.role_id;
                },
                error: (err) => {
                    this.error = 'Invalid or expired invitation link';
                }
            });
        }

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

        const userData: any = {
            email: this.email,
            password: this.password,
            full_name: this.fullName,
            org_id: Number(this.orgId)
        };

        if (this.roleId) userData.role_id = this.roleId;
        if (this.invitationToken) userData.invitation_token = this.invitationToken;

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
