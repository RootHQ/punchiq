import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MissedPunchDialogComponent } from './missed-punch-dialog.component';

describe('MissedPunchDialogComponent', () => {
  let component: MissedPunchDialogComponent;
  let fixture: ComponentFixture<MissedPunchDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MissedPunchDialogComponent]
    });
    fixture = TestBed.createComponent(MissedPunchDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
