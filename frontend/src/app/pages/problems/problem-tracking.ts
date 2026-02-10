import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProblemService, ProblemArea } from '../../services/problem.service';

@Component({
    selector: 'app-problem-tracking',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './problem-tracking.html',
    styleUrls: ['./problem-tracking.scss']
})
export class ProblemTracking implements OnInit {
    problems = signal<ProblemArea[]>([]);
    showModal = signal(false);

    newProblem = {
        branch_location: '',
        problem_type: '',
    };

    constructor(private problemService: ProblemService) { }

    ngOnInit() {
        this.loadProblems();
    }

    loadProblems() {
        this.problemService.getProblems().subscribe((data: ProblemArea[]) => {
            this.problems.set(data);
        });
    }

    onReportProblem() {
        this.problemService.createProblem(this.newProblem).subscribe({
            next: () => {
                this.loadProblems();
                this.showModal.set(false);
                this.newProblem = { branch_location: '', problem_type: '' };
            },
            error: (err: any) => console.error('Failed to report problem', err)
        });
    }

    onFix(id: number) {
        this.problemService.fixProblem(id).subscribe((updated: ProblemArea) => {
            this.problems.update((list: ProblemArea[]) => list.map(p => p.id === id ? updated : p));
        });
    }
}
