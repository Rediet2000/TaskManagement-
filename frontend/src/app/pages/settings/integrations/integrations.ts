import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IntegrationsService, GitHubIntegration, GitHubRepo, GitHubActivity } from '../../../services/integrations.service';

@Component({
    selector: 'app-integrations',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './integrations.html',
    styleUrls: ['./integrations.scss']
})
export class Integrations implements OnInit {
    private integrationsService = inject(IntegrationsService);

    integration = signal<GitHubIntegration | null>(null);
    newRepo = { github_id: 0, name: '', full_name: '', html_url: '', is_private: false };
    activities = signal<GitHubActivity[]>([]);

    webhookSecret = '';
    installationId = '';

    loading = signal(false);
    error = signal('');

    ngOnInit() {
        this.loadIntegration();
        this.loadActivity();
    }

    loadIntegration() {
        this.integrationsService.getGitHubIntegration().subscribe({
            next: (data) => this.integration.set(data),
            error: (err) => {
                if (err.status !== 404) this.error.set('Failed to load GitHub integration');
            }
        });
    }

    loadActivity() {
        this.integrationsService.getGitHubActivity().subscribe({
            next: (data) => this.activities.set(data),
            error: () => console.error('Failed to load activities')
        });
    }

    setupIntegration() {
        this.loading.set(true);
        this.integrationsService.setupGitHubIntegration({
            webhook_secret: this.webhookSecret,
            installation_id: this.installationId
        }).subscribe({
            next: (data) => {
                this.integration.set(data);
                this.loading.set(false);
                this.webhookSecret = '';
                this.installationId = '';
            },
            error: () => {
                this.error.set('Failed to setup integration');
                this.loading.set(false);
            }
        });
    }

    addRepo() {
        if (!this.newRepo.github_id || !this.newRepo.full_name) return;

        this.integrationsService.registerRepository(this.newRepo).subscribe({
            next: (repo) => {
                if (this.integration()) {
                    this.integration.set({
                        ...this.integration()!,
                        repositories: [...this.integration()!.repositories, repo]
                    });
                }
                this.newRepo = { github_id: 0, name: '', full_name: '', html_url: '', is_private: false };
            },
            error: () => this.error.set('Failed to add repository')
        });
    }
}
