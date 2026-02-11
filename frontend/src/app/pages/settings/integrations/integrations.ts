import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-integrations',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './integrations.html',
    styleUrls: ['./integrations.scss']
})
export class Integrations {
    githubToken = '';
    gitlabToken = '';
    jiraUrl = '';

    githubConnected = signal(false);
    gitlabConnected = signal(false);
    jiraConnected = signal(false);

    connectGithub() {
        // Placeholder for actual API call
        if (this.githubToken.trim()) {
            this.githubConnected.set(true);
            this.githubToken = '';
        }
    }

    disconnectGithub() {
        this.githubConnected.set(false);
    }

    connectGitlab() {
        if (this.gitlabToken.trim()) {
            this.gitlabConnected.set(true);
            this.gitlabToken = '';
        }
    }

    disconnectGitlab() {
        this.gitlabConnected.set(false);
    }

    connectJira() {
        if (this.jiraUrl.trim()) {
            this.jiraConnected.set(true);
            this.jiraUrl = '';
        }
    }

    disconnectJira() {
        this.jiraConnected.set(false);
    }
}
