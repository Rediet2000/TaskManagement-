import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReportsService } from '../../services/reports.service';

@Component({
    selector: 'app-admin-dashboard',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './admin-dashboard.html',
    styles: [`
        :host {
            --card-bg: rgba(30, 41, 59, 0.4);
            --card-border: rgba(255, 255, 255, 0.08);
            --neon-blue: #3b82f6;
            --neon-green: #10b981;
            --neon-purple: #8b5cf6;
            --neon-pink: #ec4899;
        }

        @keyframes flow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .dashboard-container {
            padding: 3rem;
            min-height: calc(100vh - 4.5rem);
            background: 
                radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 100% 100%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                #0f172a;
            position: relative;
            overflow-x: hidden;
        }

        .header-section {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 4rem;
            animation: slideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);

            h1 {
                font-family: 'Outfit', sans-serif;
                font-size: 3.5rem;
                font-weight: 800;
                letter-spacing: -0.04em;
                background: linear-gradient(to right, #fff, #94a3b8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                line-height: 1;
            }

            p {
                margin: 0.75rem 0 0;
                font-size: 1.25rem;
                color: #64748b;
                font-weight: 400;
            }
        }

        .action-group {
            display: flex;
            gap: 1rem;
        }

        .premium-btn {
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 0.75rem 1.5rem;
            border-radius: 14px;
            color: #fff;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

            &:hover {
                background: rgba(255,255,255,0.1);
                border-color: rgba(255,255,255,0.2);
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
                
                i { transform: rotate(180deg); }
            }

            i { transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2.5rem;

            @media (max-width: 768px) {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }
        }

        .stat-card {
            background: var(--card-bg);
            backdrop-filter: blur(25px);
            border: 1px solid var(--card-border);
            border-radius: 32px;
            padding: 2.5rem;
            position: relative;
            transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
            animation: slideUp 1s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;

            &::before {
                content: '';
                position: absolute;
                inset: 0;
                border-radius: 32px;
                padding: 1px;
                background: linear-gradient(135deg, rgba(255,255,255,0.2), transparent, rgba(255,255,255,0.05));
                -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor;
                mask-composite: exclude;
                opacity: 0.5;
                transition: opacity 0.5s ease;
            }

            &:hover {
                transform: translateY(-12px) scale(1.02);
                background: rgba(30, 41, 59, 0.6);
                border-color: rgba(255,255,255,0.2);
                box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.6);

                &::before { opacity: 1; }

                .stat-icon-wrapper {
                    transform: scale(1.1) translateY(-5px);
                    background: var(--accent-glow);
                    box-shadow: 0 0 30px var(--accent-glow);
                }

                .trend-line path {
                    stroke-dashoffset: 0;
                }
            }
        }

        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 2rem;
        }

        .stat-icon-wrapper {
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: var(--icon-color);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .stat-label {
            font-family: 'Outfit', sans-serif;
            font-size: 0.875rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.15em;
        }

        .stat-main {
            display: flex;
            align-items: baseline;
            gap: 1rem;
        }

        .stat-value {
            font-family: 'Outfit', sans-serif;
            font-size: 4rem;
            font-weight: 800;
            color: #fff;
            line-height: 1;
            letter-spacing: -0.02em;
        }

        .stat-trend {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--neon-green);
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .visual-container {
            margin-top: 2rem;
            height: 60px;
            position: relative;
        }

        .resource-meters {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            
            .meter-item {
                .meter-label {
                    font-size: 0.75rem;
                    color: #475569;
                    margin-bottom: 0.4rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }
            }
        }

        .trend-line {
            width: 100%;
            height: 100%;

            path {
                fill: none;
                stroke: var(--icon-color);
                stroke-width: 3;
                stroke-linecap: round;
                stroke-linejoin: round;
                stroke-dasharray: 400;
                stroke-dashoffset: 400;
                transition: stroke-dashoffset 1.5s ease-out;
            }
        }

        .stat-footer {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .footer-detail {
            font-size: 0.8125rem;
            color: #475569;
            font-weight: 500;

            strong { color: #94a3b8; }
        }

        .progress-track {
            height: 6px;
            background: rgba(255,255,255,0.05);
            border-radius: 3px;
            flex: 1;
            margin: 0 1rem;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--icon-color), #fff);
            border-radius: 3px;
            box-shadow: 0 0 15px var(--icon-color);
        }

        .pulse {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--neon-green);
            box-shadow: 0 0 10px var(--neon-green);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
    `]
})
export class AdminDashboard implements OnInit {
    private reportsService = inject(ReportsService);

    stats = signal<any>(null);
    loading = signal<boolean>(true);
    error = signal<string>('');

    ngOnInit() {
        this.loadStats();
    }

    loadStats() {
        this.loading.set(true);
        this.reportsService.getAdminStats().subscribe({
            next: (data) => {
                this.stats.set(data);
                this.loading.set(false);
            },
            error: (err) => {
                console.error('Failed to load admin stats', err);
                this.error.set('Failed to load dashboard statistics');
                this.loading.set(false);
            }
        });
    }
}
