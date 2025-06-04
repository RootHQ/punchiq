import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { PunchComponent } from './pages/punch/punch.component';
import { LogsComponent } from './pages/logs/logs.component';
import { ConfirmationPunchComponent } from './pages/confirmation-punch/confirmation-punch.component';
import { TimeOffRequestComponent } from './pages/time-off-request/time-off-request.component';

const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: ':companyId/login', component: LoginComponent },
  { path: ':companyId/punch', component: PunchComponent },
  { path: ':companyId/logs', component: LogsComponent },
  { path: ':companyId/confirmation-punch', component: ConfirmationPunchComponent}, // Assuming this is the correct route for confirmation punch
  { path: '**', redirectTo: 'login' }, // Optional: Catch-all route for invalid URLs
  { path: ':companyId/time-request', component: TimeOffRequestComponent}, // Assuming this is the correct route for confirmation punch

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
