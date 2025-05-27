import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-missed-punch-dialog',
  templateUrl: './missed-punch-dialog.component.html',
  styleUrls: ['./missed-punch-dialog.component.css']

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
