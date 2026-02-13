import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService } from '../../../services/task.service';

@Component({
    selector: 'app-integrations',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './integrations.html',
    styleUrls: ['./integrations.scss']
})
export class Integrations {
    private taskService = inject(TaskService);
    private storageKeyPrefix = 'integration_connected_';

    githubToken = '';
    gitlabToken = '';
    jiraUrl = '';

    githubConnected = signal(false);
    gitlabConnected = signal(false);
    jiraConnected = signal(false);

    testTaskId = '';
    testStatus = signal('');

    constructor() {
        this.githubConnected.set(localStorage.getItem(this.storageKeyPrefix + 'github') === 'true');
        this.gitlabConnected.set(localStorage.getItem(this.storageKeyPrefix + 'gitlab') === 'true');
        this.jiraConnected.set(localStorage.getItem(this.storageKeyPrefix + 'jira') === 'true');
    }

    connectGithub() {
        // Placeholder for actual API call
        if (this.githubToken.trim()) {
            this.githubConnected.set(true);
            localStorage.setItem(this.storageKeyPrefix + 'github', 'true');
            this.githubToken = '';
        }
    }

    disconnectGithub() {
        this.githubConnected.set(false);
        localStorage.removeItem(this.storageKeyPrefix + 'github');
    }

    testGithub() {
        if (!this.testTaskId) {
            this.testStatus.set('Error: Task ID required');
            return;
        }

        this.testStatus.set('Transmitting mock webhook...');
        this.taskService.testGitHubConnection(parseInt(this.testTaskId)).subscribe({
            next: (res) => {
                this.testStatus.set(`Success: Processed ${res.processed_commits} commits.`);
                this.testTaskId = '';
            },
            error: (err) => {
                this.testStatus.set('Error: Webhook transmission failed');
                console.error(err);
            }
        });
    }

    connectGitlab() {
        if (this.gitlabToken.trim()) {
            this.gitlabConnected.set(true);
            localStorage.setItem(this.storageKeyPrefix + 'gitlab', 'true');
            this.gitlabToken = '';
        }
    }

    disconnectGitlab() {
        this.gitlabConnected.set(false);
        localStorage.removeItem(this.storageKeyPrefix + 'gitlab');
    }

    connectJira() {
        if (this.jiraUrl.trim()) {
            this.jiraConnected.set(true);
            localStorage.setItem(this.storageKeyPrefix + 'jira', 'true');
            this.jiraUrl = '';
        }
    }

    disconnectJira() {
        this.jiraConnected.set(false);
        localStorage.removeItem(this.storageKeyPrefix + 'jira');
    }
}
