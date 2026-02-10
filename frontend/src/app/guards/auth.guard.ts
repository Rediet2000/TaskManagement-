import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take } from 'rxjs';

export const authGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    return authService.currentUser.pipe(
        take(1),
        map(user => {
            if (user) {
                return true;
            }

            // Not logged in, redirect to login page with the return url
            router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
            return false;
        })
    );
};
