import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    {
        path: 'login',
        loadComponent: () => import('./pages/login/login').then(m => m.Login)
    },
    {
        path: 'signup',
        loadComponent: () => import('./pages/signup/signup').then(m => m.SignUp)
    },
    {
        path: 'register-company',
        loadComponent: () => import('./pages/signup/register-company').then(m => m.RegisterCompany)
    },
    {
        path: 'forgot-password',
        loadComponent: () => import('./pages/login/forgot-password').then(m => m.ForgotPassword)
    },
    {
        path: 'reset-password',
        loadComponent: () => import('./pages/login/reset-password').then(m => m.ResetPassword)
    },
    {
        path: '',
        loadComponent: () => import('./layout/main-layout/main-layout').then(m => m.MainLayout),
        canActivate: [authGuard],
        children: [
            {
                path: '',
                loadComponent: () => import('./pages/dashboard/dashboard').then(m => m.Dashboard)
            },
            {
                path: 'tasks',
                loadComponent: () => import('./pages/tasks/task-board').then(m => m.TaskBoard)
            },
            {
                path: 'agile',
                loadComponent: () => import('./pages/tasks/agile-board').then(m => m.AgileBoard)
            },
            {
                path: 'problems',
                loadComponent: () => import('./pages/problems/problem-tracking').then(m => m.ProblemTracking)
            },
            {
                path: 'rbac',
                loadComponent: () => import('./pages/hierarchy/hierarchy-manager').then(m => m.HierarchyManager)
            },
            {
                path: 'analytics',
                loadComponent: () => import('./pages/analytics/analytics').then(m => m.Analytics)
            },
            {
                path: 'settings',
                loadComponent: () => import('./pages/settings/settings').then(m => m.Settings)
            },
            {
                path: 'settings/integrations',
                loadComponent: () => import('./pages/settings/integrations/integrations').then(m => m.Integrations)
            },
            {
                path: 'profile',
                loadComponent: () => import('./pages/profile/profile').then(m => m.Profile)
            },
            {
                path: 'reports',
                loadComponent: () => import('./pages/reports/reports').then(m => m.Reports)
            },
            {
                path: 'admin-dashboard',
                loadComponent: () => import('./pages/dashboard/admin-dashboard').then(m => m.AdminDashboard)
            },
            {
                path: 'notes',
                loadComponent: () => import('./pages/notes/notes').then(m => m.NotesPage)
            },
            {
                path: 'security',
                loadComponent: () => import('./pages/security/security-logs').then(m => m.SecurityLogs)
            },
            {
                path: 'archive',
                loadComponent: () => import('./pages/tasks/archive-management').then(m => m.ArchiveManagement)
            },
            // Add more feature routes here
        ]
    },
    {
        path: '**',
        redirectTo: ''
    }
];
