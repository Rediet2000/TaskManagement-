import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
    selector: 'app-analytics',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './analytics.html',
    styleUrls: ['./analytics.scss']
})
export class Analytics implements OnInit {
    insights = signal<any>(null);

    constructor(private http: HttpClient) { }

    ngOnInit() {
        this.http.get(`${environment.apiUrl}/reports`).subscribe(data => {
            this.insights.set(data);
        });
    }
}
