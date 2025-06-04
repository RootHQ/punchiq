import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimeOffRequestComponent } from './time-off-request.component';

describe('TimeOffRequestComponent', () => {
  let component: TimeOffRequestComponent;
  let fixture: ComponentFixture<TimeOffRequestComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TimeOffRequestComponent]
    });
    fixture = TestBed.createComponent(TimeOffRequestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
