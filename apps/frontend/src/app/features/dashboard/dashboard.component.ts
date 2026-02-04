import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { StravaService, StravaActivity } from '../../core/services/strava.service';

interface DashboardStats {
  totalActivities: number;
  totalDistance: number;
  totalTime: number;
  totalElevation: number;
  thisWeekActivities: number;
  thisWeekDistance: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  private stravaService = inject(StravaService);

  stats = signal<DashboardStats>({
    totalActivities: 0,
    totalDistance: 0,
    totalTime: 0,
    totalElevation: 0,
    thisWeekActivities: 0,
    thisWeekDistance: 0
  });

  recentActivities = signal<StravaActivity[]>([]);
  loading = signal(true);
  isConnected = signal(false);

  ngOnInit() {
    this.isConnected.set(this.stravaService.isAuthenticated());
    
    if (this.isConnected()) {
      this.loadRealData();
    } else {
      this.loading.set(false);
    }
  }

  private loadRealData() {
    this.loading.set(true);
    
    // Load recent activities
    this.stravaService.getActivities(1, 5).subscribe({
      next: (activities) => {
        this.recentActivities.set(activities);
        this.calculateStats(activities);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading activities:', err);
        this.loading.set(false);
      }
    });
  }

  private calculateStats(activities: StravaActivity[]) {
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    const thisWeekActivities = activities.filter(a => 
      new Date(a.start_date) >= weekAgo
    );

    this.stats.set({
      totalActivities: activities.length,
      totalDistance: activities.reduce((sum, a) => sum + a.distance, 0),
      totalTime: activities.reduce((sum, a) => sum + a.moving_time, 0),
      totalElevation: activities.reduce((sum, a) => sum + a.total_elevation_gain, 0),
      thisWeekActivities: thisWeekActivities.length,
      thisWeekDistance: thisWeekActivities.reduce((sum, a) => sum + a.distance, 0)
    });
  }

  formatDistance(meters: number): string {
    return (meters / 1000).toFixed(1);
  }

  formatTime(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  formatPace(distance: number, time: number): string {
    if (distance === 0) return '-';
    const paceSeconds = time / (distance / 1000);
    const minutes = Math.floor(paceSeconds / 60);
    const seconds = Math.floor(paceSeconds % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')} /km`;
  }

  getActivityIcon(type: string): string {
    switch (type.toLowerCase()) {
      case 'run': return '🏃';
      case 'ride': return '🚴';
      case 'swim': return '🏊';
      default: return '🏋️';
    }
  }
}
