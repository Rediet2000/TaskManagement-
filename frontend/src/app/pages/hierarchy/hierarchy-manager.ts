import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HierarchyService, Department, Team, Organization, OrganizationCreate, Branch } from '../../services/hierarchy.service';
import { AuthService } from '../../services/auth.service';
import { RbacService, Role, Permission } from '../../services/rbac.service';

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
    permissions = signal<Permission[]>([]);
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
    newRole: any = { name: '', parent_role_id: null, permission_ids: [] };
    editRoleData: any = { id: 0, name: '', parent_role_id: null, permission_ids: [] };
    newBranch = { name: '', address: '' };
    newOrg = { name: '', primary_color: '#2563eb', secondary_color: '#64748b' };

    currentOrgId: number | null = null;
    isSuperAdmin = signal(false);
    success = signal('');
    error = signal('');

    private autoDismiss() {
        setTimeout(() => {
            this.success.set('');
            this.error.set('');
        }, 5000);
    }

    ngOnInit() {
        const user = this.authService.currentUser();
        if (!user) return;

        this.currentOrgId = user.org_id;

        // Robust check for superadmin/admin status
        const role = user.role_name || user.role?.name;
        this.isSuperAdmin.set(role === 'Super Admin' || role === 'Admin');

        this.loadData();
    }

    loadData() {
        this.hierarchyService.getBranches().subscribe((branches: Branch[]) => this.branches.set(branches));
        this.hierarchyService.getDepartments().subscribe((depts: Department[]) => this.departments.set(depts));
        this.hierarchyService.getTeams().subscribe((teams: Team[]) => this.teams.set(teams));
        this.rbacService.getRoles().subscribe((roles: Role[]) => this.roles.set(roles));
        this.rbacService.getPermissions().subscribe((perms: Permission[]) => this.permissions.set(perms));

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
                this.success.set('Department created successfully');
                this.error.set('');
                this.loadData();
                this.autoDismiss();
                this.showDeptModal.set(false);
                this.newDept = { name: '' };
            },
            error: (err: any) => {
                this.error.set(err.error?.detail || 'Failed to create department');
                console.error('Failed to create department', err);
            }
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
                this.success.set('Team created successfully');
                this.error.set('');
                this.loadData();
                this.showTeamModal.set(false);
                this.newTeam.name = '';
            },
            error: (err: any) => {
                this.error.set(err.error?.detail || 'Failed to create team');
                console.error('Failed to create team', err);
            }
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
                this.success.set('Role created successfully');
                this.error.set('');
                this.loadData();
                this.autoDismiss();
                this.showRoleModal.set(false);
                this.newRole = { name: '', parent_role_id: null };
            },
            error: (err: any) => {
                this.error.set(err.error?.detail || 'Failed to create role');
                console.error('Failed to create role', err);
            }
        });
    }

    openEditRoleModal(role: Role) {
        this.editRoleData = {
            id: role.id,
            name: role.name,
            parent_role_id: role.parent_role_id,
            permission_ids: (role as any).permissions?.map((p: any) => p.id) || []
        };
        this.showEditRoleModal.set(true);
    }

    onUpdateRole() {
        if (!this.editRoleData.name) return;
        this.rbacService.updateRole(this.editRoleData.id, {
            name: this.editRoleData.name,
            parent_role_id: this.editRoleData.parent_role_id,
            permission_ids: this.editRoleData.permission_ids
        }).subscribe({
            next: () => {
                this.success.set('Role updated successfully');
                this.loadData();
                this.showEditRoleModal.set(false);
                this.autoDismiss();
            },
            error: (err: any) => {
                this.error.set(err.error?.detail || 'Failed to update role');
                console.error('Failed to update role', err);
            }
        });
    }

    togglePermission(permId: number) {
        const index = this.editRoleData.permission_ids.indexOf(permId);
        if (index > -1) {
            this.editRoleData.permission_ids.splice(index, 1);
        } else {
            this.editRoleData.permission_ids.push(permId);
        }
    }

    isPermissionSelected(permId: number): boolean {
        return this.editRoleData.permission_ids.includes(permId);
    }

    onDeleteRole(roleId: number) {
        if (!confirm('Are you sure you want to delete this role?')) return;
        this.rbacService.deleteRole(roleId).subscribe({
            next: () => {
                this.success.set('Role deleted successfully');
                this.error.set('');
                this.loadData();
            },
            error: (err: any) => {
                this.error.set(err.error?.detail || 'Failed to delete role');
                alert(err.error?.detail || 'Failed to delete role');
            }
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
