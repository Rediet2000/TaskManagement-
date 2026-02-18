import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CalendarComponent } from '../../components/calendar/calendar';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
    selector: 'app-calendar-page',
    standalone: true,
    imports: [CommonModule, CalendarComponent, TranslatePipe],
    templateUrl: './calendar.html',
    styleUrls: ['./calendar.scss']
})
export class CalendarPage { }
