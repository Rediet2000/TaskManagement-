import { Directive, Input, TemplateRef, ViewContainerRef, inject, OnInit, OnDestroy, effect } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Subscription } from 'rxjs';

@Directive({
    selector: '[appHasPermission]',
    standalone: true
})
export class HasPermissionDirective implements OnInit, OnDestroy {
    private authService = inject(AuthService);
    private templateRef = inject(TemplateRef<any>);
    private viewContainer = inject(ViewContainerRef);

    private requiredPermission = '';
    private hasView = false;

    constructor() {
        effect(() => {
            // Access signal to register dependency
            this.authService.currentUser();
            this.updateView();
        });
    }

    @Input()
    set appHasPermission(permission: string) {
        this.requiredPermission = permission;
        this.updateView();
    }

    ngOnInit() { }

    ngOnDestroy() { }

    private updateView() {
        // If no permission strictly required (empty string), show it? 
        // Or assume it's always required if directive is used?
        // Let's assume required.

        // Wait until user is not null? 
        // If not logged in, authService.hasPermission returns false.

        if (this.authService.hasPermission(this.requiredPermission)) {
            if (!this.hasView) {
                this.viewContainer.createEmbeddedView(this.templateRef);
                this.hasView = true;
            }
        } else {
            if (this.hasView) {
                this.viewContainer.clear();
                this.hasView = false;
            }
        }
    }
}
