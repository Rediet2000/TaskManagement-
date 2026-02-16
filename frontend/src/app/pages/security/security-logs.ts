import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SecurityService, AuditLog } from '../../services/security.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-security-logs',
    standalone: true,
    imports: [CommonModule, TranslatePipe],
    templateUrl: './security-logs.html',
    styleUrls: ['./security-logs.scss']
})
export class SecurityLogs implements OnInit {
    logs = signal<AuditLog[]>([]);
    loading = signal(false);

    constructor(private securityService: SecurityService) { }

    ngOnInit() {
        this.loadLogs();
    }

    loadLogs() {
        this.loading.set(true);
        this.securityService.getLogs().subscribe({
            next: (data) => {
                this.logs.set(data);
                this.loading.set(false);
            },
            error: (err) => {
                console.error('Failed to load security logs', err);
                this.loading.set(false);
            }
        });
    }
}
