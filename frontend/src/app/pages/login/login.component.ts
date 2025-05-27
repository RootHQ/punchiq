import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  companyId = '';
  employeeId = '';
  pin = '';
  error = '';
  showPin = false;
  isLoading = false;

  constructor(
    private authService: AuthService, 
    private route: ActivatedRoute, 
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.companyId = params.get('companyId') || '';
    });

    this.route.queryParams.subscribe(query => {
      if (query['expired']) {
        this.error = 'Your session has expired. Please log in again.';
      }
    });
  }

  onLogin(): void {
    this.isLoading = true;
    this.error = '';
  
    this.authService.login(this.employeeId, this.pin, this.companyId).subscribe({
      next: (res) => {
        this.isLoading = false;
        localStorage.setItem('auth_token', res.token);
        localStorage.setItem('employee_name', res.employee_name);
        localStorage.setItem('punch_status', res.punch_status);
        localStorage.setItem('employee_id', res.employee_id);
        
        localStorage.setItem('punch_in_time', res.punch_in_time);
        localStorage.setItem('break_start_time', res.break_start_time);
        localStorage.setItem('break_end_time', res.break_end_time);
        localStorage.setItem('punch_out_time', res.punch_out_time);
 
        
        this.navigateBasedOnPunchStatus(res.punch_status);
      },
      error: (err) => {
        this.isLoading = false;
        console.error('Login failed:', err);
        this.error = err?.error?.message || 'The login information you entered is incorrect.';
      }
    });
  }

  navigateBasedOnPunchStatus(punchStatus: string): void {
    const baseRoute = `/${this.companyId}`;

    const routesMap: { [key: string]: string } = {
      'NOT_PUNCHED_IN': `${baseRoute}/punch`,
      'PUNCHED_IN': `${baseRoute}/punch`,
      'ON_BREAK': `${baseRoute}/punch`,
      'FINISHED_BREAK': `${baseRoute}/punch`,
      'PUNCHED_OUT': `${baseRoute}/punch`
    };
   /* const routesMap: { [key: string]: string } = {
      'NOT_PUNCHED_IN': `${baseRoute}/punch`,
      'PUNCHED_IN': `${baseRoute}/break`,
      'ON_BREAK': `${baseRoute}/resume-work`,
      'FINISHED_BREAK': `${baseRoute}/resume-work`,
      'PUNCHED_OUT': `${baseRoute}/summary`
    };*/

    const targetRoute = routesMap[punchStatus] || `${baseRoute}/punch`;
    console.log('Navigating to:', targetRoute);
    this.router.navigate([targetRoute]);
  }

  togglePinVisibility(): void {
    this.showPin = !this.showPin;
  }
}
