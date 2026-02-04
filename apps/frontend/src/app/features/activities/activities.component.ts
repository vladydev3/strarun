import { Component, signal, inject, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { StravaService, StravaActivity } from '../../core/services/strava.service';

@Component({
  selector: 'app-activities',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './activities.component.html',
  styleUrl: './activities.component.scss'
})
export class ActivitiesComponent implements OnInit {
  private stravaService = inject(StravaService);

  activities = signal<StravaActivity[]>([]);
  loading = signal(true);
  filter = signal<'all' | 'run' | 'ride' | 'swim'>('all');
  sortBy = signal<'date' | 'distance' | 'time'>('date');
  isConnected = signal(false);
  currentPage = signal(1);
  hasMore = signal(true);

  ngOnInit() {
    this.isConnected.set(this.stravaService.isAuthenticated());
    
    if (this.isConnected()) {
      this.loadActivities();
    } else {
      this.loading.set(false);
    }
  }

  loadActivities() {
    this.loading.set(true);
    
    this.stravaService.getActivities(this.currentPage(), 30).subscribe({
      next: (activities) => {
        if (this.currentPage() === 1) {
          this.activities.set(activities);
        } else {
          this.activities.update(current => [...current, ...activities]);
        }
        this.hasMore.set(activities.length === 30);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading activities:', err);
        this.loading.set(false);
      }
    });
  }

  loadMore() {
    if (this.hasMore() && !this.loading()) {
      this.currentPage.update(p => p + 1);
      this.loadActivities();
    }
  }

  setFilter(filter: 'all' | 'run' | 'ride' | 'swim') {
    this.filter.set(filter);
  }

  setSortBy(sort: 'date' | 'distance' | 'time') {
    this.sortBy.set(sort);
  }

  get filteredActivities(): StravaActivity[] {
    let list = this.activities();
    
    // Filter by type
    if (this.filter() !== 'all') {
      list = list.filter(a => a.type.toLowerCase() === this.filter());
    }
    
    // Sort
    switch (this.sortBy()) {
      case 'distance':
        list = [...list].sort((a, b) => b.distance - a.distance);
        break;
      case 'time':
        list = [...list].sort((a, b) => b.moving_time - a.moving_time);
        break;
      default:
        list = [...list].sort((a, b) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime());
    }
    
    return list;
  }

  formatDistance(meters: number): string {
    return (meters / 1000).toFixed(2) + ' km';
  }

  formatDuration(seconds: number): string {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hrs > 0) {
      return `${hrs}h ${mins}m`;
    }
    return `${mins}m ${secs}s`;
  }

  formatPace(speedMs: number, type: string): string {
    if (speedMs === 0) return '-';
    if (type === 'Swim') {
      // min/100m for swimming
      const pace = 100 / speedMs / 60;
      return `${pace.toFixed(0)}:${Math.round((pace % 1) * 60).toString().padStart(2, '0')} /100m`;
    } else if (type === 'Run') {
      // min/km for running
      const pace = 1000 / speedMs / 60;
      const mins = Math.floor(pace);
      const secs = Math.round((pace - mins) * 60);
      return `${mins}:${secs.toString().padStart(2, '0')} /km`;
    }
    // km/h for cycling
    return `${(speedMs * 3.6).toFixed(1)} km/h`;
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
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
