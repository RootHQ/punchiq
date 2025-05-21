import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-confirmation-punch',
  templateUrl: './confirmation-punch.component.html',
  styleUrls: ['./confirmation-punch.component.css']
})
export class ConfirmationPunchComponent {
  punchStatus: string = ''; // Possible values: 'NONE', 'break_start', 'break_end_time', 'punch_out_time'
  companyId = '';
  punchInTime = '';
  breakStartTime = '';
  breakEndTime = '';
  punchOutTime = '';

  countdownSeconds = 5;
  countdownInterval: any;
  messageShowPunch = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.companyId = params.get('companyId') || '';
    });
    
      this.punchInTime = localStorage.getItem('punch_in_time') || '';
      this.breakStartTime = localStorage.getItem('break_start_time') || '';
      this.breakEndTime = localStorage.getItem('break_end_time') || '';
      this.punchOutTime = localStorage.getItem('punch_out_time') || '';

    
      this.updatePunchStatus();
      console.log('Punch Status:', this.punchStatus);
      
      this.fetchAffirmation();
      this.startCountdown();
      

  }

  fetchAffirmation() {
  /*  fetch('/api/affirmation')
    .then(response => response.json())
    .then(data => {
      
      console.log('Affirmation:', data.affirmation);
      this.messageShowPunch = data.affirmation || 'Stay positive!';
    })
    .catch(err => console.error('Error fetching affirmation:', err));
*/
  fetch('https://tzpddlbp4d.execute-api.us-east-2.amazonaws.com/Test/DailyAffirmation2')
    .then(response => response.json())
    .then(data => {
      console.log('Affirmation:', data.affirmation);
      this.messageShowPunch = data.affirmation || 'Stay positive!';
    })
    .catch(err => console.error('Error fetching affirmation:', err));
    }
  
  startCountdown(): void {
    this.countdownInterval = setInterval(() => {
      this.countdownSeconds--;
      if (this.countdownSeconds === 0) {
        clearInterval(this.countdownInterval);
        console.log('🔓 Unlocking and redirecting after 5 seconds...');
        this.onLogout();
      }
    }, 1000);
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
    
    console.log('Punch Status finished:', this.punchStatus);
  }

  isValidTime(value: any): boolean {
    const isValid = value != null && value !== '' && value !== 'null';
    return isValid;
  }

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/' + this.companyId + '/login']);
  }
}


