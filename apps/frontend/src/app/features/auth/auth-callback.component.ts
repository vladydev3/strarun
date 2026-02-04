import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { StravaService } from '../../core/services/strava.service';

@Component({
  selector: 'app-auth-callback',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="callback-container">
      @if (loading) {
        <div class="loading">
          <div class="spinner"></div>
          <p>Connecting to Strava...</p>
        </div>
      } @else if (error) {
        <div class="error">
          <h2>Connection Failed</h2>
          <p>{{ error }}</p>
          <button (click)="retry()">Try Again</button>
        </div>
      }
    </div>
  `,
  styles: [`
    .callback-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: var(--color-background);
    }

    .loading {
      text-align: center;
    }

    .spinner {
      width: 48px;
      height: 48px;
      border: 4px solid var(--color-border);
      border-top-color: var(--color-primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 1rem;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error {
      text-align: center;
      padding: 2rem;
      background: var(--color-surface);
      border-radius: var(--radius-lg);
      
      h2 {
        color: #dc3545;
        margin-bottom: 0.5rem;
      }
      
      p {
        color: var(--color-text-muted);
        margin-bottom: 1rem;
      }
      
      button {
        padding: 0.75rem 1.5rem;
        background: var(--color-primary);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        cursor: pointer;
      }
    }
  `]
})
export class AuthCallbackComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private stravaService = inject(StravaService);

  loading = true;
  error: string | null = null;

  ngOnInit() {
    const code = this.route.snapshot.queryParamMap.get('code');
    const errorParam = this.route.snapshot.queryParamMap.get('error');

    if (errorParam) {
      this.loading = false;
      this.error = 'Authorization was denied or cancelled.';
      return;
    }

    if (!code) {
      this.loading = false;
      this.error = 'No authorization code received.';
      return;
    }

    this.exchangeCode(code);
  }

  private exchangeCode(code: string) {
    this.stravaService.exchangeToken(code).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Failed to connect to Strava. Please try again.';
        console.error('Token exchange error:', err);
      }
    });
  }

  retry() {
    window.location.href = this.stravaService.getAuthUrl();
  }
}
