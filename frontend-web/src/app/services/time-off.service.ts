
// time-off.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class TimeOffService {
  private apiUrl = 'https://tzpddlbp4d.execute-api.us-east-2.amazonaws.com/Test/Time-Request';

  constructor(private http: HttpClient) {}

  sendRequest(data: any): Observable<any> {
    return this.http.post(this.apiUrl, data);
  }
}
