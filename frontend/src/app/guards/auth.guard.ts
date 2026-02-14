import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { filter, map, switchMap, take } from 'rxjs';
import { toObservable } from '@angular/core/rxjs-interop';

export const authGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    // Wait for initialization if it's still in progress
    const isInit$ = toObservable(authService.isInitialized);

    return isInit$.pipe(
        filter(init => init === true),
        switchMap(() => authService.currentUser$),
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
