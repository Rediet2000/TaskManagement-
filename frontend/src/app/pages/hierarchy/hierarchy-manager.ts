import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HierarchyService, Department, Team, Organization, OrganizationCreate, Branch } from '../../services/hierarchy.service';
import { AuthService } from '../../services/auth.service';
import { RbacService, Role } from '../../services/rbac.service';

@Component({
    selector: 'app-hierarchy-manager',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './hierarchy-manager.html',
    styleUrls: ['./hierarchy-manager.scss']
})
export class HierarchyManager implements OnInit {
    private hierarchyService = inject(HierarchyService);
    private authService = inject(AuthService);
    private rbacService = inject(RbacService);

    departments = signal<Department[]>([]);
    teams = signal<Team[]>([]);
    roles = signal<Role[]>([]);
    organizations = signal<Organization[]>([]);
    branches = signal<Branch[]>([]);

    showDeptModal = signal(false);
    showTeamModal = signal(false);
    showRoleModal = signal(false);
    showOrgModal = signal(false);
    showEditRoleModal = signal(false);
    showBranchModal = signal(false);

    newDept = { name: '' };
    newTeam = { name: '', dept_id: 0 };
    newRole: any = { name: '', parent_role_id: null };
    editRoleData: any = { id: 0, name: '', parent_role_id: null };
    newBranch = { name: '', address: '' };
    newOrg = { name: '', primary_color: '#2563eb', secondary_color: '#64748b' };

    currentOrgId: number | null = null;
    isSuperAdmin = signal(false);

    ngOnInit() {
        const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
        this.currentOrgId = user.org_id;
        // Simple check for superadmin
        this.isSuperAdmin.set(user.role_id === 1);
        this.loadData();
    }

    loadData() {
        this.hierarchyService.getBranches().subscribe((branches: Branch[]) => this.branches.set(branches));
        this.hierarchyService.getDepartments().subscribe((depts: Department[]) => this.departments.set(depts));
        this.hierarchyService.getTeams().subscribe((teams: Team[]) => this.teams.set(teams));
        this.rbacService.getRoles().subscribe((roles: Role[]) => this.roles.set(roles));
        if (this.isSuperAdmin()) {
            this.hierarchyService.getOrganizations().subscribe((orgs: Organization[]) => this.organizations.set(orgs));
        }
    }

    getTeamsByDept(deptId: number) {
        return this.teams().filter(t => (t as any).dept_id === deptId);
    }

    getRoleName(roleId: number | null | undefined): string {
        if (!roleId) return '';
        const role = this.roles().find(r => r.id === roleId);
        return role ? role.name : '';
    }

    getBranchName(branchId: number | null | undefined): string {
        if (!branchId) return 'No Branch';
        const branch = this.branches().find(b => b.id === branchId);
        return branch ? branch.name : 'Unknown Branch';
    }

    getDeptsByBranch(branchId: number | null) {
        return this.departments().filter(d => (d as any).branch_id === branchId);
    }

    onAddDept() {
        if (!this.currentOrgId) return;
        this.hierarchyService.createDepartment({
            name: this.newDept.name,
            org_id: this.currentOrgId,
            branch_id: (this.newDept as any).branch_id
        }).subscribe({
            next: () => {
                this.loadData();
                this.showDeptModal.set(false);
                this.newDept = { name: '' };
            },
            error: (err: any) => console.error('Failed to create department', err)
        });
    }

    openDeptModal(branchId: number | null = null) {
        (this.newDept as any).branch_id = branchId;
        this.showDeptModal.set(true);
    }

    onAddTeam() {
        if (!this.currentOrgId) return;
        this.hierarchyService.createTeam({
            name: this.newTeam.name,
            dept_id: this.newTeam.dept_id,
            org_id: this.currentOrgId
        }).subscribe({
            next: () => {
                this.loadData();
                this.showTeamModal.set(false);
                this.newTeam.name = '';
            },
            error: (err: any) => console.error('Failed to create team', err)
        });
    }

    openTeamModal(deptId: number) {
        this.newTeam.dept_id = deptId;
        this.showTeamModal.set(true);
    }

    onAddRole() {
        if (!this.currentOrgId) return;
        this.rbacService.createRole({
            name: this.newRole.name,
            parent_role_id: this.newRole.parent_role_id,
            org_id: this.currentOrgId
        }).subscribe({
            next: () => {
                this.loadData();
                this.showRoleModal.set(false);
                this.newRole = { name: '', parent_role_id: null };
            },
            error: (err: any) => console.error('Failed to create role', err)
        });
    }

    openEditRoleModal(role: Role) {
        this.editRoleData = { id: role.id, name: role.name, parent_role_id: role.parent_role_id };
        this.showEditRoleModal.set(true);
    }

    onUpdateRole() {
        if (!this.editRoleData.name) return;
        this.rbacService.updateRole(this.editRoleData.id, {
            name: this.editRoleData.name,
            parent_role_id: this.editRoleData.parent_role_id
        }).subscribe({
            next: () => {
                this.loadData();
                this.showEditRoleModal.set(false);
            },
            error: (err: any) => alert(err.error?.detail || 'Failed to update role')
        });
    }

    onDeleteRole(roleId: number) {
        if (!confirm('Are you sure you want to delete this role?')) return;
        this.rbacService.deleteRole(roleId).subscribe({
            next: () => this.loadData(),
            error: (err: any) => alert(err.error?.detail || 'Failed to delete role')
        });
    }

    onAddBranch() {
        if (!this.currentOrgId) return;
        this.hierarchyService.createBranch({
            name: this.newBranch.name,
            address: this.newBranch.address,
            org_id: this.currentOrgId
        }).subscribe({
            next: () => {
                this.loadData();
                this.showBranchModal.set(false);
                this.newBranch = { name: '', address: '' };
            },
            error: (err: any) => console.error('Failed to create branch', err)
        });
    }

    onAddOrg() {
        if (!this.newOrg.name) return;
        this.hierarchyService.createOrganization(this.newOrg).subscribe({
            next: () => {
                this.loadData();
                this.showOrgModal.set(false);
                this.newOrg = { name: '', primary_color: '#2563eb', secondary_color: '#64748b' };
            },
            error: (err: any) => console.error('Failed to create organization', err)
        });
    }
}
