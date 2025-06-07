import { Component, OnInit, OnDestroy } from '@angular/core';
import { ConfettiService } from '../../services/confetti.service';

@Component({
  standalone: true,
  selector: 'app-confetti',
  template: `
    <div class="container"></div>
  `,
  styles: [`
    .container {
      text-align: center;
      margin-top: 100px;
    }
  `]
})
export class ConfettiComponent implements OnInit, OnDestroy {
  private confettiInterval: any;
  private fireCount = 0;
  private maxFires = 2; // 🎯 Launch 2 times

  constructor(private confettiService: ConfettiService) {}

  ngOnInit() {
    this.startTimedConfetti();
  }

  ngOnDestroy() {
    this.stopConfetti();
  }

  startTimedConfetti() {
    this.fireCount = 0;

    this.confettiInterval = setInterval(() => {
      this.confettiService.launchConfetti();
      this.fireCount++;

      if (this.fireCount >= this.maxFires) {
        this.stopConfetti();
      }
    }, 1000); 
  }

  stopConfetti() {
    if (this.confettiInterval) {
      clearInterval(this.confettiInterval);
      this.confettiInterval = null;
    }
  }
}
