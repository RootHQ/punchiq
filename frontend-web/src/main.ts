import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Routes } from '@angular/router';
import { LoginComponent } from './app/pages/login/login.component';
import { AppComponent } from './app/app.component';
import { ConfirmationPunchComponent } from './app/pages/confirmation-punch/confirmation-punch.component';
import { PunchComponent } from './app/pages/punch/punch.component';
import { TimeOffRequestComponent } from './app/pages/time-off-request/time-off-request.component';

const routes: Routes = [
    { path: '', redirectTo: 'login', pathMatch: 'full' },
      { path: ':companyId/login', component: LoginComponent },
      { path: ':companyId/punch', component: PunchComponent },
      { path: ':companyId/confirmation-punch', component: ConfirmationPunchComponent}, 
      { path: '**', redirectTo: 'login' }, 
      { path: ':companyId/time-request', component: TimeOffRequestComponent}
];


bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(),
    provideRouter(routes)
  ]
});