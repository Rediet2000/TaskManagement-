import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterLink, TranslatePipe],
    templateUrl: './login.html',
    styleUrls: ['./login.scss']
})
export class Login {
    email = '';
    password = '';
    error = '';
    loading = false;

    private authService = inject(AuthService);
    private router = inject(Router);
    public route = inject(ActivatedRoute);

    onSubmit() {
        this.loading = true;
        this.error = '';

        this.authService.login(this.email, this.password).subscribe({
            next: () => {
                this.authService.getMe().subscribe(() => {
                    const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
                    this.router.navigate([returnUrl]);
                });
            },
            error: err => {
                this.error = err.error?.detail || 'Invalid email or password';
                this.loading = false;
            }
        });
    }
}
