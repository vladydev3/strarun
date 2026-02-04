import { Component, signal, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StravaService, StravaActivity, AthleteStats } from '../../core/services/strava.service';

interface WeeklyStats {
  week: string;
  distance: number;
  time: number;
  activities: number;
  elevation: number;
}

interface MonthlyStats {
  month: string;
  distance: number;
  time: number;
  activities: number;
}

@Component({
  selector: 'app-stats',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stats.component.html',
  styleUrl: './stats.component.scss'
})
export class StatsComponent implements OnInit {
  private stravaService = inject(StravaService);

  loading = signal(true);
  isConnected = signal(false);
  selectedPeriod = signal<'week' | 'month' | 'year'>('month');
  
  yearToDate = signal({
    totalDistance: 0,
    totalTime: 0,
    totalActivities: 0,
    totalElevation: 0,
    longestRun: 0,
    fastestPace: ''
  });

  weeklyStats = signal<WeeklyStats[]>([]);
  monthlyStats = signal<MonthlyStats[]>([]);

  ngOnInit() {
    this.isConnected.set(this.stravaService.isAuthenticated());
    
    if (this.isConnected()) {
      this.loadStats();
    } else {
      this.loading.set(false);
    }
  }

  loadStats() {
    this.loading.set(true);
    const athlete = this.stravaService.currentAthlete();
    
    if (!athlete) {
      this.loading.set(false);
      return;
    }

    this.stravaService.getAthleteStats(athlete.id).subscribe({
      next: (stats) => {
        this.processAthleteStats(stats);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading stats:', err);
        this.loading.set(false);
      }
    });

    // Also load activities to calculate weekly/monthly breakdown
    this.stravaService.getActivities(1, 100).subscribe({
      next: (activities) => {
        this.calculateWeeklyMonthlyStats(activities);
      }
    });
  }

  private processAthleteStats(stats: AthleteStats) {
    const runTotals = stats.ytd_run_totals;
    const rideTotals = stats.ytd_ride_totals;

    this.yearToDate.set({
      totalDistance: (runTotals?.distance || 0) + (rideTotals?.distance || 0),
      totalTime: (runTotals?.moving_time || 0) + (rideTotals?.moving_time || 0),
      totalActivities: (runTotals?.count || 0) + (rideTotals?.count || 0),
      totalElevation: (runTotals?.elevation_gain || 0) + (rideTotals?.elevation_gain || 0),
      longestRun: stats.biggest_ride_distance || 0,
      fastestPace: '-'
    });
  }

  private calculateWeeklyMonthlyStats(activities: StravaActivity[]) {
    const weeklyMap = new Map<string, WeeklyStats>();
    const monthlyMap = new Map<string, MonthlyStats>();

    activities.forEach(activity => {
      const date = new Date(activity.start_date);
      
      // Weekly grouping
      const weekStart = this.getWeekStart(date);
      const weekKey = weekStart.toISOString().split('T')[0];
      const weekLabel = this.formatWeekLabel(weekStart);
      
      if (!weeklyMap.has(weekKey)) {
        weeklyMap.set(weekKey, { week: weekLabel, distance: 0, time: 0, activities: 0, elevation: 0 });
      }
      const weekStats = weeklyMap.get(weekKey)!;
      weekStats.distance += activity.distance;
      weekStats.time += activity.moving_time;
      weekStats.activities++;
      weekStats.elevation += activity.total_elevation_gain;

      // Monthly grouping
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthLabel = date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      
      if (!monthlyMap.has(monthKey)) {
        monthlyMap.set(monthKey, { month: monthLabel, distance: 0, time: 0, activities: 0 });
      }
      const monthStats = monthlyMap.get(monthKey)!;
      monthStats.distance += activity.distance;
      monthStats.time += activity.moving_time;
      monthStats.activities++;
    });

    // Sort and limit
    this.weeklyStats.set(
      Array.from(weeklyMap.values())
        .sort((a, b) => b.week.localeCompare(a.week))
        .slice(0, 4)
    );

    this.monthlyStats.set(
      Array.from(monthlyMap.values())
        .sort((a, b) => b.month.localeCompare(a.month))
        .slice(0, 6)
    );
  }

  private getWeekStart(date: Date): Date {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  }

  private formatWeekLabel(weekStart: Date): string {
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 6);
    return `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  }

  setPeriod(period: 'week' | 'month' | 'year') {
    this.selectedPeriod.set(period);
  }

  formatDistance(meters: number): string {
    return (meters / 1000).toFixed(1) + ' km';
  }

  formatDuration(seconds: number): string {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  }

  getMaxDistance(): number {
    const stats = this.selectedPeriod() === 'week' 
      ? this.weeklyStats() 
      : this.monthlyStats();
    if (stats.length === 0) return 0;
    return Math.max(...stats.map(s => s.distance));
  }

  getBarWidth(distance: number): number {
    const max = this.getMaxDistance();
    return max > 0 ? (distance / max) * 100 : 0;
  }
}
