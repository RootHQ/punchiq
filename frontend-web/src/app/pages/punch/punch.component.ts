import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MatDialog } from '@angular/material/dialog';
import { PunchService } from '../../services/punch.service';
import { jwtDecode } from 'jwt-decode';
import { MissedPunchDialogComponent } from '../missed-punch-dialog/missed-punch-dialog.component';

export interface JwtPayload {
  sub: string;
  pin_encrypted: string;
  empName: string;
  company_id: string;
  exp: number;
  punch_in_time: string;
  break_start_time: string;
  break_end_time: string;
  punch_out_time: string;
}

@Component({
  standalone: true,
  selector: 'app-punch',
  templateUrl: './punch.component.html',
  styleUrls: ['./punch.component.css'],
  imports: [RouterModule,CommonModule]
})
export class PunchComponent {
  companyId = '';
  employeeId = '';
  employeeName = '';
  typeBreak = '';
  pin = '';
  error = '';
  companyName = '';

  punchInTime = '';
  breakStartTime = '';
  breakEndTime = '';
  punchOutTime = '';
  punchStatus: string = ''; // Possible values: 'NONE', 'break_start', 'break_end_time', 'punch_out_time'
  punchStatusTemporal: boolean = false;
  isLoading = false;

  
  constructor(
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog,
    private punchService: PunchService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.companyId = params.get('companyId') || '';
      console.log('[punch] companyId:', this.companyId);
      
    });

    this.route.queryParams.subscribe(() => {
      const token = this.authService.getToken();
      
      if (token) {
        
        const payload = jwtDecode<JwtPayload>(token);
        const exp = payload.exp * 1000;
        const currentTime = Date.now();
        const minutesLeft = (exp - currentTime) / (1000 * 60);

        if (minutesLeft > 0 && minutesLeft <= 5) {
         // this.dialog.open(SessionExpirationDialogComponent, {
         //   data: { minutes: Math.floor(minutesLeft) },
          //  width: '400px'
         // });
        }

        if (currentTime >= exp) {
          this.authService.logout();
          this.router.navigate(['/' + this.companyId + '/login'], { queryParams: { expired: true } });
          return;
        }

        this.employeeId = payload.sub || '';
        this.employeeName = payload.empName || '';
        this.pin = atob(payload.pin_encrypted || '');
        this.companyName = payload.company_id || '';
        this.typeBreak = localStorage.getItem('punch_status') || '';
        
        // New Time Fields
        this.punchInTime = localStorage.getItem('punch_in_time') || '';
        this.breakStartTime = localStorage.getItem('break_start_time') || '';
        this.breakEndTime = localStorage.getItem('break_end_time') || '';
        this.punchOutTime = localStorage.getItem('punch_out_time') || '';

        // Debugging logs
        console.log('punchInTime:', this.punchInTime);
        console.log('breakStartTime:', this.breakStartTime);
        console.log('breakEndTime:', this.breakEndTime);
        console.log('punchOutTime:', this.punchOutTime);
        

        // Persist to localStorage if needed
        localStorage.setItem('employee_id', this.employeeId);
        localStorage.setItem('employee_name', this.employeeName);
        localStorage.setItem('pin', this.pin);
        localStorage.setItem('company_name', this.companyName);

        localStorage.setItem('requesstTimeOff','');

        this.updatePunchStatus();
        
      } else {
        this.authService.logout();
        this.router.navigate(['/' + this.companyId + '/login'], { queryParams: { expired: true } });
      }
    });
  }
  getLastPunchTime(): string {
    let lastTime = '';
    let lastLabel = '';
  
    if (this.isValidTime(this.punchInTime)) {
      lastTime = this.punchInTime;
      lastLabel = 'Punch In';
      console.log('punchInTime lastTime:', lastTime);

    }
  
    if (this.isValidTime(this.breakStartTime)) {
      lastTime = this.breakStartTime;
      lastLabel = 'Break Start';
      console.log('Break Start lastTime:', lastTime);

    }
  
    if (this.isValidTime(this.breakEndTime)) {
      lastTime = this.breakEndTime;
      lastLabel = 'Break End';
      console.log('Break End lastTime:', lastTime);
    }
  
    if (this.isValidTime(this.punchOutTime)) {
      lastTime = this.punchOutTime;
      lastLabel = 'Punch Out';
      console.log('Punch Out lastTime:', lastTime);

    }
  
    if (!lastTime) {
      return 'Your last recorded punch: No punches yet';
    }
    
    const date = this.toDate(lastTime);
  
    const formattedTime = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,  
    });

    return `Your last recorded punch: ${formattedTime} (${lastLabel})`;
  }

  toDate(timeStr: string): Date {
  const today = new Date();
  const [hour, minute] = timeStr.split(':').map(Number);
  return new Date(today.getFullYear(), today.getMonth(), today.getDate(), hour, minute);
}
  
  isValidTime(value: any): boolean {
    const isValid = value != null && value !== '' && value !== 'null';
    return isValid;
  }

  updatePunchStatus() {
    
    this.punchStatus = 'NONE'; // Default status

    if (this.isValidTime(this.punchInTime)) {
      this.punchStatus = 'punchInTime';
    }
  
    if (this.isValidTime(this.breakStartTime)) {
      this.punchStatus = 'breakStartTime';
      
    }
  
    if (this.isValidTime(this.breakEndTime)) {
      this.punchStatus = 'breakEndTime';
    }
  
    if (this.isValidTime(this.punchOutTime)) {
      this.punchStatus = 'punchOutTime';

    }
    
    console.log('Punch Status:', this.punchStatus);
  }

  updatePunchStatusTemp(punchStatusTemporal: boolean = false) {
    
    if ( this.punchStatus = 'NONE') {
      this.punchStatus = 'punchInTime';
    }

    if (this.isValidTime(this.punchInTime)) {
      this.punchStatus = 'breakStartTime';
    }
  
    if (this.isValidTime(this.breakStartTime)) {
      this.punchStatus = 'breakEndTime';
      
    }
  
    if (this.isValidTime(this.breakEndTime)) {
      this.punchStatus = 'punchOutTime';
    }
  
    console.log('Punch Status Temporal:', this.punchStatus);
  }

  onMissedPunch() {
    const lastPunchTime = this.getLastPunchTime();
    

    const dialogRef = this.dialog.open(MissedPunchDialogComponent, {
      data: { lastPunchTime: lastPunchTime },
      width: '500px', 
      panelClass: 'custom-dialog-container'
    });
  
    dialogRef.afterClosed().subscribe(result => {
      if (result === 'confirm') {
        console.log('Missed Punch Confirmed');
        this.punchStatusTemporal = true;
        
        this.updatePunchStatusTemp(this.punchStatusTemporal);
        
        this.router.navigate([this.router.url]);

      } else {
        console.log('Missed Punch Canceled');
      }
    });
  }

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/' + this.companyId + '/login']);
  }
  onPunch() {
    localStorage.removeItem('requestTimeOff');
    this.sendPunch('punchIn');
  }

  sendPunch(action: string) {
    const currentDate = new Date();
    const formattedDate = currentDate.toISOString().split('T')[0]; // YYYY-MM-DD
    const formattedTime = currentDate.toTimeString().split(' ')[0].substring(0, 5); // HH:MM
    localStorage.removeItem('requestTimeOff');
    this.isLoading = true;

    // Fetch Public IP Address
    fetch('https://api.ipify.org?format=json')
      .then(response => response.json())
      .then(data => {
        const ipAddress = data.ip;
  
        const punchData: any = {
          employeeId: this.employeeId,
          companyId: this.companyId,
          netsuiteId: null,
          Date: formattedDate,
          punch_in_time: '',
          punch_out_time: '',
          break_start_time: '',
          break_end_time: '',
          ip_address: ipAddress // Include IP here
        };
  
        switch (action) {
          case 'punchIn':
            punchData.punch_in_time = formattedTime;
            localStorage.setItem('punch_in_time', formattedTime);
            break;
          case 'breakStart':
            punchData.break_start_time = formattedTime;
            localStorage.setItem('break_start_time', formattedTime);
            break;
          case 'breakEnd':
            punchData.break_end_time = formattedTime;
            localStorage.setItem('break_end_time', formattedTime);
            break;
          case 'punchOut':
            punchData.punch_out_time = formattedTime;
            localStorage.setItem('punch_out_time', formattedTime);
            break;
          default:
            console.error('Invalid action:', action);
            return;
        }
        console.log('Punch Data:', action);
        localStorage.setItem('punch_status', action);
  
        // Send Punch with IP
        this.punchService.updatePunch(punchData).subscribe({
          next: (response: any) => {
            console.log('✅ Punch updated successfully:', response);
  
            // Update Local Variables
            this.punchInTime = localStorage.getItem('punch_in_time') || '';
            this.breakStartTime = localStorage.getItem('break_start_time') || '';
            this.breakEndTime = localStorage.getItem('break_end_time') || '';
            this.punchOutTime = localStorage.getItem('punch_out_time') || '';
            this.typeBreak = action;
  
            this.updatePunchStatus();
            this.isLoading = false;
          },
          error: (error: any) => {
            this.isLoading = false;
            console.error('❌ Error updating punch:', error);
            this.error = 'Failed to update punch. Please try again.';
          }
        });
        const baseRoute = `/${this.companyId}`;

        const targetRoute =  `${baseRoute}/confirmation-punch`;
        console.log('Navigating to:', targetRoute);
        this.router.navigate([targetRoute]);
      })
      .catch(error => {
        this.isLoading = false;
        console.error('❌ Failed to fetch IP address:', error);
        this.error = 'Unable to get IP address.';
      });
  }
}
