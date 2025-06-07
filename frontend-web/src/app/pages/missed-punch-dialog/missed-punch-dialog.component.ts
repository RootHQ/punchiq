import { CommonModule } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';

@Component({
  standalone: true,
  selector: 'app-missed-punch-dialog',
  templateUrl: './missed-punch-dialog.component.html',
  styleUrls: ['./missed-punch-dialog.component.css'],
  imports: [
    CommonModule,
    MatDialogModule,   
    MatButtonModule ]

})
export class MissedPunchDialogComponent {
  lastPunchTime: string;

  constructor(
    public dialogRef: MatDialogRef<MissedPunchDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.lastPunchTime = data.lastPunchTime;
  }

  onCancel() {
    this.dialogRef.close('cancel');
  }

  onConfirm() {
    this.dialogRef.close('confirm');
  }
}
