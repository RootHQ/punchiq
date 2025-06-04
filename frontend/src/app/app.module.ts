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
import { MissedPunchDialogComponent } from './pages/missed-punch-dialog/missed-punch-dialog.component';
import { ConfirmationPunchComponent } from './pages/confirmation-punch/confirmation-punch.component';
import { ConfettiComponent } from './pages/confetti/confetti.component';
import { TimeOffRequestComponent } from './pages/time-off-request/time-off-request.component';

import { MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBarModule} from '@angular/material/snack-bar'; 
import { ConfirmDialogComponent } from './pages/confirm-dialog/confirm-dialog.component';
import { MatFormFieldModule } from '@angular/material/form-field';

import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatPaginatorModule } from '@angular/material/paginator';
    
@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    PunchComponent,
    LogsComponent,
    MissedPunchDialogComponent,
    ConfirmationPunchComponent,
    ConfettiComponent,
    TimeOffRequestComponent,
    ConfirmDialogComponent,
   
    
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatTableModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatDatepickerModule,
    MatNativeDateModule,
    FormsModule,
    MatSnackBarModule,
    MatPaginatorModule,
    MatFormFieldModule,
    MatTooltipModule,
    MatCheckboxModule

  ],
  providers: [
    {
      provide: HttpClientModule,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
