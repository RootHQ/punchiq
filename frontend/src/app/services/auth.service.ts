import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { jwtDecode } from 'jwt-decode';
import { Observable, tap } from 'rxjs';

interface JwtPayload {
  exp: number;
  [key: string]: any;
}
@Injectable({
  providedIn: 'root'
})

export class AuthService {
  private apiUrl = 'https://st7tfw3sl3.execute-api.us-east-2.amazonaws.com/default/login2';
  private TOKEN_KEY = 'auth_token';
  private USER_KEY = 'employee_name';
  private COMPANY_KEY = 'company_id';
  
  constructor(private http: HttpClient) {}

  login(employeeId: string, pin: string, company_id: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, {
      employee_id: employeeId,
      pin: pin,
      company_id: company_id
    }).pipe(
      tap(response => {
        console.log('[Login response]', response); 
        if (response.token && response.employee_name && company_id) {
          this.saveSession(response.token, response.employee_name, company_id);
        } else {
          console.warn('Missing fields in response:', response);
        }
      })
    );
  }
  

  isTokenExpired(): boolean {
    const token = this.getToken();
    if (!token) {
      console.warn('No token found');
      return true;
    }
  
    try {
      const decoded = jwtDecode<JwtPayload>(token);
      const currentTime = Math.floor(Date.now() / 1000);
      const expired = decoded.exp < currentTime;
      if (expired) {
        console.warn('Token has expired');
      }
      return expired;
    } catch (e) {
      console.error('Invalid token format:', e);
      return true;
    }
  }
  

  private saveSession(token: string, name: string, company_id: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, name);
    localStorage.setItem(this.COMPANY_KEY, company_id);
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getEmployeeName(): string | null {
    return localStorage.getItem(this.USER_KEY);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}
