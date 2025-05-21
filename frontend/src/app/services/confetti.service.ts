// src/app/services/confetti.service.ts
import { Injectable } from '@angular/core';
import confetti from 'canvas-confetti';

@Injectable({
  providedIn: 'root',
})
export class ConfettiService {
  launchConfetti() {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
    });
  }

  launchWideConfetti() {
    confetti({
      particleCount: 200,
      spread: 180,
      origin: { y: 0.5 },
    });
  }

  launchContinuousConfetti(durationMs: number = 5000) {
    const end = Date.now() + durationMs;

    (function frame() {
      confetti({
        particleCount: 7,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
      });
      confetti({
        particleCount: 7,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
      });

      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    })();
  }
}
