import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';

import { LoginComponent } from './pages/login/login.component';
import { PunchComponent } from './pages/punch/punch.component';
import { LogsComponent } from './pages/logs/logs.component';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { MissedPunchDialogComponent } from './pages/missed-punch-dialog/missed-punch-dialog.component';
import { ConfirmationPunchComponent } from './pages/confirmation-punch/confirmation-punch.component';
import { ConfettiComponent } from './pages/confetti/confetti.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    PunchComponent,
    LogsComponent,
    MissedPunchDialogComponent,
    ConfirmationPunchComponent,
    ConfettiComponent,
    
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
