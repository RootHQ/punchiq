import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PunchService {
  private apiUrl = 'https://tzpddlbp4d.execute-api.us-east-2.amazonaws.com/prod/InsertUpdatePunchSdddQS';

  constructor(private http: HttpClient) {}

  updatePunch(data: any): Observable<any> {
    return this.http.put(this.apiUrl, data);
  }
}
