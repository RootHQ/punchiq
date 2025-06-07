import { Component, OnInit, ViewChild,ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TimeOffService } from '../../services/time-off.service';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { jwtDecode } from 'jwt-decode';
import { MatDatepicker } from '@angular/material/datepicker';
import { MatTable } from '@angular/material/table';

import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule, MatOptionModule } from '@angular/material/core'; // para soporte de fechas
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import {  MatFormFieldModule } from '@angular/material/form-field';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { RouterModule } from '@angular/router';


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
const  COLUMNS_SCHEMA = [
    { key: 'date', label: 'Date', type: 'date' },
    { key: 'payCode', label: 'Pay Code', type: 'payCode' },
    { key: 'length', label: 'Length', type: 'length' },
    { key: 'notes', label: 'Notes', type: 'notes' },
    { key: 'isEdit', label: '', type: 'isEdit' }
  ];

@Component({
  standalone: true,
  selector: 'app-time-off-request',
  templateUrl: './time-off-request.component.html',
  styleUrls: ['./time-off-request.component.css'],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatOptionModule,
    MatSnackBarModule,   
    MatDialogModule,      
    MatDatepickerModule,  
    MatNativeDateModule,  
    MatTableModule,       
    MatIconModule,        
    MatButtonModule   ,
    RouterModule  
  ]
})
export class TimeOffRequestComponent implements OnInit {
  displayedColumns = COLUMNS_SCHEMA.map(c => c.key);
  columnsSchema = COLUMNS_SCHEMA;
  dataSource: any[] = [];
  companyId: string = '';
  employeeId: string = '';
  currentEditingElement: any = null;
  datePickerRefs: { [key: string]: any } = {};
  pickerRefs: any[] = [];
  
  @ViewChild(MatTable) table!: MatTable<any>;
  
  constructor(
    private  readonly authService: AuthService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    public dialog: MatDialog,
    private readonly snackBar: MatSnackBar,
    private readonly timeOffService: TimeOffService,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
          this.companyId = params.get('companyId') || '';
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
          
            
            
          } else {
            this.authService.logout();
            this.router.navigate(['/' + this.companyId + '/login'], { queryParams: { expired: true } });
          }
        });

        this.addRow();
  }

  addRow() {
    const newRow = {
      id: this.generateId(),
      isEdit: true,
      date: new Date(),
      payCode: 1,     
      length: 4,        
      notes: ''
    };
    this.dataSource.push(newRow);
    this.dataSource = [...this.dataSource];
  }
  generateId(): number {
    return Math.floor(Math.random() * 1000000);
  }
  saveRow(row: any) {
      row.isEdit = false;
  }

 removeRow(id: number) {
  const index = this.dataSource.findIndex(row => row.id === id);
  if (index >= 0) {
    const updatedData = [...this.dataSource];  
    updatedData.splice(index, 1);             
    this.dataSource = updatedData;             
    this.pickerRefs.splice(index, 1);         
     this.cdr.detectChanges();
  }
}

  submit() {
    let isValid = true;

    this.dataSource.forEach((row: any) => {
      row.errors = {};

      if (!row.date) {
        row.errors.date = true;
        isValid = false;
      }

      if (!row.payCode) {
        row.errors.payCode = true;
        isValid = false;
      }

      if (!row.length) {
        row.errors.length = true;
        isValid = false;
      }

      if (!row.notes || row.notes.trim().length < 5) {
        row.errors.notes = true;
        isValid = false;
      }

      row.isEdit = true;
    });

    if (!isValid) {
      console.warn('Invalid data, please check the highlighted fields.');
      this.showSuccessMessage('Please, complete all required fields.', 'error');
      this.cdr.detectChanges();
      return;
    }

    const timeOffRequests = this.dataSource.map(row => ({
      date: row.date.toISOString().split('T')[0],
      payCode: row.payCode,
      length: row.length,
      notes: row.notes
    }));

    const requestData = {
      employeeId: this.employeeId,
      companyId: this.companyId,
      timeOffRequests: timeOffRequests
    };

    if (!requestData.timeOffRequests || requestData.timeOffRequests.length === 0) {
      console.warn('No time-off requests to submit.');
      this.showSuccessMessage('You don’t have any valid time-off requests to submit.', 'error');
      return;
    }

    this.timeOffService.sendRequest(requestData).subscribe({
      next: (response) => {
        console.log('Time off requests submitted successfully:', response);
        this.dataSource = [];
        this.cdr.detectChanges();
        localStorage.setItem('requestTimeOff', 'sent');

        const baseRoute = `/${this.companyId}`;

        const targetRoute =  `${baseRoute}/confirmation-punch`;
        console.log('Navigating to:', targetRoute);
        this.router.navigate([targetRoute]);
      },
      error: (error) => {
        console.error('Error submitting time off requests:', error);
        localStorage.setItem('requestTimeOff','')
        this.showSuccessMessage('Error submitting time off requests, contact administrator.', 'error');
      }
    });
  }

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/' + this.companyId + '/login']);
  }

  openPicker(picker: any, element: any) {
    this.currentEditingElement = element;
    picker.open();
  }

  onDateClosed(event: any) {
    console.log('Calendario cerrado');
    setTimeout(() => event.close(), 0);
  }

  registerPickerRef(id: number, picker: any) {
    this.datePickerRefs[id] = picker;
  }

  onDateSelected(picker: MatDatepicker<Date>, element: any) {
    
    picker.close();
    element.isEdit=false;
    console.log('Date :', element.date);
  
    element.date = new Date(element.date);  
    this.cdr.detectChanges(); 

    element.isEdit=true;
  }

  getPayCodeLabel(value: string | number): string {
    const map: { [key: string]: string } = {
      '1': 'Vacation',
      '2': 'Non-Paid' 
    };
    return map[String(value)] || String(value);
  }

  getLabelForLength(value: string | number): string {
    const map: { [key: string]: string } = {
      '4': '4 hours',
      '8': '8 hours' 
    };
   return map[String(value)] || String(value);
  }

  showSuccessMessage(message: string, type: 'success' | 'error' = 'success'): void {
    this.snackBar.open(message, '', {
      duration: 3000,
      panelClass: [type === 'success' ? 'success-snackbar' : 'error-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom'
    });
  }

 
}
