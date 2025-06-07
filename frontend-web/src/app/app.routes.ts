import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { ConfirmationPunchComponent } from './pages/confirmation-punch/confirmation-punch.component';
import { PunchComponent } from './pages/punch/punch.component';
import { TimeOffRequestComponent } from './pages/time-off-request/time-off-request.component';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: ':companyId/login', component: LoginComponent },
  { path: ':companyId/punch', component: PunchComponent },
  { path: ':companyId/confirmation-punch', component: ConfirmationPunchComponent}, // Assuming this is the correct route for confirmation punch
  { path: '**', redirectTo: 'login' }, // Optional: Catch-all route for invalid URLs
  { path: ':companyId/time-request', component: TimeOffRequestComponent}, // Assuming this is the correct route for confirmation punch

];
