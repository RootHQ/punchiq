import { Component, OnInit, ViewChild, ChangeDetectorRef } from '@angular/core';
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
import { MatNativeDateModule, MatOptionModule } from '@angular/material/core';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
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

const COLUMNS_SCHEMA = [
  { key: 'date', label: 'Date', type: 'date' },
  { key: 'payCode', label: 'Pay Code', type: 'payCode' },
  { key: 'length', label: 'Length', type: 'length' },
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
    MatButtonModule,
    RouterModule
  ]
})
export class TimeOffRequestComponent implements OnInit {
 displayedColumns = ['date', 'payCode', 'length'];
  isMainRow = (index: number, row: any) => !row.isNotes;
  isNotesRow = (index: number, row: any) => row.isNotes;
  columnsSchema = COLUMNS_SCHEMA;
  filteredColumns = ['date', 'payCode', 'length', 'isEdit'];
  dataSource: any[] = [];
  companyId: string = '';
  employeeId: string = '';
  currentEditingElement: any = null;
  datePickerRefs: { [key: string]: any } = {};
  pickerRefs: any[] = [];

  @ViewChild(MatTable) table!: MatTable<any>;

  constructor(
    private readonly authService: AuthService,
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
    this.filteredColumns = this.displayedColumns.filter(c => c !== 'notes');

    if (token) {
      const payload = jwtDecode<JwtPayload>(token);
      const exp = payload.exp * 1000;
      const currentTime = Date.now();

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
  const mainRow = {
    id: Date.now(),
    date: null,
    payCode: null,
    length: null,
    notes: '',
    isNotes: false
  };
  const notesRow = {
    ...mainRow,
    isNotes: true
  };
  this.dataSource.push(mainRow, notesRow);
  this.dataSource = [...this.dataSource];
}

  generateId(): number {
    return Math.floor(Math.random() * 1000000);
  }

  removeRow(id: number) {
  const index = this.dataSource.findIndex(row => row.id === id && !row.isNotes);

  if (index >= 0) {
    this.dataSource.splice(index, 2);
    this.dataSource = [...this.dataSource];
  }
}

 submit() {
  let isValid = true;

  this.dataSource.forEach(row => {
    row.errors = {};

    if (!row.date && !row.isNotes) {
      row.errors.date = true;
      isValid = false;
    }
    if (!row.payCode && !row.isNotes) {
      row.errors.payCode = true;
      isValid = false;
    }
    if (!row.length && !row.isNotes) {
      row.errors.length = true;
      isValid = false;
    }
    if (row.notes && row.notes.trim().length > 0 && row.notes.trim().length < 5) {
      row.errors.notes = true;
      isValid = false;
    }

    row.isEdit = true;
  });

  console.log('Data source after validation:', this.dataSource);
  if (!isValid) {
    this.snackBar.open('Please correct the errors before submitting.', '', {
      duration: 3000,
      panelClass: ['error-snackbar']
    });
    return;
  }

  const groupedRequests = this.dataSource
    .filter(row => !row.isNotes)
    .map(mainRow => {
      const notesRow = this.dataSource.find(r => r.isNotes && r.id === mainRow.id);
      return {
        date: mainRow.date.toISOString().split('T')[0],
        payCode: mainRow.payCode,
        length: mainRow.length,
        notes: notesRow?.notes || ''
      };
    });

  const requestData = {
    employeeId: this.employeeId,
    companyId: this.companyId,
    timeOffRequests: groupedRequests
  };

  this.timeOffService.sendRequest(requestData).subscribe({
    next: () => {
      this.snackBar.open('Request submitted successfully!', '', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
      this.dataSource = [];
      this.addRow();
       localStorage.setItem('requestTimeOff', 'sent');

    },
    error: () => {
      this.snackBar.open('Error submitting request.', '', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
  });

  setTimeout(() => {
    this.router.navigate(['/', this.companyId, 'confirmation-punch']);
  }, 2000);
}


  onLogout() {
    this.authService.logout();
    this.router.navigate(['/' + this.companyId + '/login']);
  }

  onDateSelected(picker: MatDatepicker<Date>, element: any) {
    picker.close();
    element.date = new Date(element.date);
    this.cdr.detectChanges();
  }

  getPayCodeLabel(value: string | number): string {
    return { '1': 'Vacation', '2': 'Non-Paid' }[String(value)] || String(value);
  }

  getLabelForLength(value: string | number): string {
    return { '4': '4 hours', '8': '8 hours' }[String(value)] || String(value);
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
