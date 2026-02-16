import { Component, OnInit, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TaskService, Task } from '../../services/task.service';
import { NotesService, Note } from '../../services/notes.service';
import { forkJoin } from 'rxjs';
import { TranslatePipe } from '../../pipes/translate.pipe';

interface CalendarDay {
    date: Date;
    isCurrentMonth: boolean;
    isToday: boolean;
    tasks: Task[];
    notes: Note[];
}

@Component({
    selector: 'app-calendar',
    standalone: true,
    imports: [CommonModule, TranslatePipe],
    templateUrl: './calendar.html',
    styleUrls: ['./calendar.scss']
})
export class CalendarComponent implements OnInit {
    private taskService = inject(TaskService);
    private notesService = inject(NotesService);

    currentDate = signal(new Date());
    days = signal<CalendarDay[]>([]);

    selectedDay = signal<CalendarDay | null>(null);

    monthName = computed(() => {
        return this.currentDate().toLocaleString('default', { month: 'long', year: 'numeric' });
    });

    ngOnInit() {
        this.generateCalendar();
    }

    generateCalendar() {
        const date = this.currentDate();
        const year = date.getFullYear();
        const month = date.getMonth();

        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);

        const startDay = firstDayOfMonth.getDay(); // 0 = Sunday
        const prevMonthLastDay = new Date(year, month, 0).getDate();

        const calendarDays: CalendarDay[] = [];

        // Previous month days
        for (let i = startDay - 1; i >= 0; i--) {
            const d = new Date(year, month - 1, prevMonthLastDay - i);
            calendarDays.push(this.createDay(d, false));
        }

        // Current month days
        for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
            const d = new Date(year, month, i);
            calendarDays.push(this.createDay(d, true));
        }

        // Next month days
        const remainingDays = 42 - calendarDays.length;
        for (let i = 1; i <= remainingDays; i++) {
            const d = new Date(year, month + 1, i);
            calendarDays.push(this.createDay(d, false));
        }

        this.days.set(calendarDays);
        this.fetchItems();
    }

    createDay(date: Date, isCurrentMonth: boolean): CalendarDay {
        const today = new Date();
        return {
            date,
            isCurrentMonth,
            isToday: date.toDateString() === today.toDateString(),
            tasks: [],
            notes: []
        };
    }

    fetchItems() {
        const date = this.currentDate();
        const start = new Date(date.getFullYear(), date.getMonth(), 1).toISOString();
        const end = new Date(date.getFullYear(), date.getMonth() + 1, 0).toISOString();

        forkJoin({
            tasks: this.taskService.getTasks(),
            notes: this.notesService.getNotes()
        }).subscribe(({ tasks, notes }) => {
            const updatedDays = this.days().map(day => {
                const dayStr = day.date.toDateString();
                return {
                    ...day,
                    tasks: tasks.filter(t => t.due_date && new Date(t.due_date).toDateString() === dayStr),
                    notes: notes.filter(n => n.reminder_at && new Date(n.reminder_at).toDateString() === dayStr)
                };
            });
            this.days.set(updatedDays);
        });
    }

    prevMonth() {
        const d = this.currentDate();
        this.currentDate.set(new Date(d.getFullYear(), d.getMonth() - 1, 1));
        this.generateCalendar();
    }

    nextMonth() {
        const d = this.currentDate();
        this.currentDate.set(new Date(d.getFullYear(), d.getMonth() + 1, 1));
        this.generateCalendar();
    }

    selectDay(day: CalendarDay) {
        this.selectedDay.set(day);
    }
}
