import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { StravaService, ActivityDetail, Lap, Split } from '../../../core/services/strava.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-activity-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './activity-detail.component.html',
  styleUrl: './activity-detail.component.scss'
})
export class ActivityDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private stravaService = inject(StravaService);
  
  activity = signal<ActivityDetail | null>(null);
  laps = signal<Lap[]>([]);
  loading = signal(true);
  isConnected = signal(false);
  activeTab = signal<'overview' | 'splits' | 'laps'>('overview');

  ngOnInit() {
    this.isConnected.set(this.stravaService.isAuthenticated());
    
    const id = this.route.snapshot.paramMap.get('id');
    if (id && this.isConnected()) {
      this.loadActivity(parseInt(id, 10));
    } else {
      this.loading.set(false);
    }
  }

  loadActivity(id: number) {
    this.loading.set(true);

    // Load activity detail and laps in parallel
    forkJoin({
      activity: this.stravaService.getActivityDetail(id),
      laps: this.stravaService.getActivityLaps(id)
    }).subscribe({
      next: ({ activity, laps }) => {
        this.activity.set(activity);
        this.laps.set(laps);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading activity:', err);
        this.loading.set(false);
      }
    });
  }

  get splits(): Split[] {
    return this.activity()?.splits_metric || [];
  }

  setActiveTab(tab: 'overview' | 'splits' | 'laps') {
    this.activeTab.set(tab);
  }

  formatDistance(meters: number): string {
    return (meters / 1000).toFixed(2) + ' km';
  }

  formatDuration(seconds: number): string {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  formatPace(speedMs: number): string {
    const pace = 1000 / speedMs / 60;
    const mins = Math.floor(pace);
    const secs = Math.round((pace - mins) * 60);
    return `${mins}:${secs.toString().padStart(2, '0')} /km`;
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getActivityIcon(type: string): string {
    const icons: Record<string, string> = {
      'Run': '🏃',
      'Ride': '🚴',
      'Swim': '🏊',
      'Walk': '🚶',
      'Hike': '🥾'
    };
    return icons[type] || '🏋️';
  }
}
