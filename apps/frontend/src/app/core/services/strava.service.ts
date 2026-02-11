import { Injectable, inject, signal } from '@angular/core';
import { Observable, tap, throwError } from 'rxjs';
import { ApiService } from './api.service';
import { CacheService } from './cache.service';
import { environment } from '../../../environments/environment';

export interface StravaAthlete {
  id: number;
  firstname: string;
  lastname: string;
  profile: string;
  profile_medium: string;
  city: string;
  state: string;
  country: string;
}

export interface StravaActivity {
  id: number;
  name: string;
  type: string;
  sport_type: string;
  start_date: string;
  start_date_local: string;
  distance: number;
  moving_time: number;
  elapsed_time: number;
  total_elevation_gain: number;
  average_speed: number;
  max_speed: number;
  average_heartrate?: number;
  max_heartrate?: number;
  average_cadence?: number;
  kudos_count: number;
  comment_count: number;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  expires_at: number;
  athlete: StravaAthlete;
}

export interface AuthStatus {
  authenticated: boolean;
  strava_connected: boolean;
  message: string;
  refresh_available?: boolean;
  athlete_name?: string;
  athlete?: StravaAthlete;
}

export interface AthleteStats {
  biggest_ride_distance: number;
  biggest_climb_elevation_gain: number;
  recent_ride_totals: ActivityTotals;
  recent_run_totals: ActivityTotals;
  recent_swim_totals: ActivityTotals;
  ytd_ride_totals: ActivityTotals;
  ytd_run_totals: ActivityTotals;
  ytd_swim_totals: ActivityTotals;
  all_ride_totals: ActivityTotals;
  all_run_totals: ActivityTotals;
  all_swim_totals: ActivityTotals;
}

export interface ActivityTotals {
  count: number;
  distance: number;
  moving_time: number;
  elapsed_time: number;
  elevation_gain: number;
}

export interface ActivityDetail {
  id: number;
  name: string;
  type: string;
  sport_type: string;
  start_date: string;
  start_date_local: string;
  timezone?: string;
  description?: string;
  distance: number;
  moving_time: number;
  elapsed_time: number;
  total_elevation_gain: number;
  average_speed: number;
  max_speed: number;
  average_heartrate?: number;
  max_heartrate?: number;
  average_cadence?: number;
  calories?: number;
  kudos_count?: number;
  comment_count?: number;
  splits_metric?: Split[];
  laps?: Lap[];
}

export interface Split {
  distance: number;
  elapsed_time: number;
  moving_time: number;
  average_speed: number;
  elevation_difference: number;
  average_heartrate?: number;
  split: number;
}

export interface Lap {
  id: number;
  name: string;
  elapsed_time: number;
  moving_time: number;
  distance: number;
  average_speed: number;
  max_speed: number;
  average_heartrate?: number;
  max_heartrate?: number;
  lap_index: number;
}

@Injectable({
  providedIn: 'root'
})
export class StravaService {
  private api = inject(ApiService);
  private cache = inject(CacheService);
  
  isAuthenticated = signal(false);
  currentAthlete = signal<StravaAthlete | null>(null);

  constructor() {
    this.checkAuthStatus();
  }

  private checkAuthStatus(): void {
    this.api.get<AuthStatus>('/api/auth/status').subscribe({
      next: status => {
        if (status.authenticated) {
          this.isAuthenticated.set(true);
          this.currentAthlete.set(status.athlete ?? null);
        } else if (status.refresh_available) {
          // Access token expired but refresh token is available; attempt refresh
          this.refreshToken().subscribe({
            next: token => {
              // Refresh successful; athlete info already updated by refreshToken's tap
              this.isAuthenticated.set(true);
              if (token.athlete) {
                this.currentAthlete.set(token.athlete);
              }
            },
            error: () => {
              // Refresh failed; user needs to re-authenticate
              this.isAuthenticated.set(false);
              this.currentAthlete.set(null);
            }
          });
        } else {
          this.isAuthenticated.set(false);
          this.currentAthlete.set(null);
        }
      },
      error: () => {
        this.isAuthenticated.set(false);
        this.currentAthlete.set(null);
      }
    });
  }

  getAuthUrl(): Observable<{auth_url: string, state: string}> {
    return this.api.get<{auth_url: string, state: string}>('/api/auth/strava');
  }

  initiateAuth(): void {
    this.getAuthUrl().subscribe({
      next: (response) => {
        // Store state for validation on callback
        sessionStorage.setItem('oauth_state', response.state);
        // Redirect to Strava
        window.location.href = response.auth_url;
      },
      error: (err) => {
        console.error('Failed to get auth URL:', err);
      }
    });
  }

  exchangeToken(code: string, state?: string): Observable<AuthToken> {
    // Validate state if provided
    if (state) {
      const storedState = sessionStorage.getItem('oauth_state');
      if (!storedState || storedState !== state) {
        sessionStorage.removeItem('oauth_state');
        return throwError(() => new Error('OAuth state validation failed. This may indicate a security issue or expired authentication request. Please try signing in again.'));
      }
      sessionStorage.removeItem('oauth_state');
    }
    
    return this.api.post<AuthToken>('/api/auth/token', { code }).pipe(
      tap(token => {
        this.isAuthenticated.set(true);
        this.currentAthlete.set(token.athlete);
      })
    );
  }

  refreshToken(): Observable<AuthToken> {
    return this.api.post<AuthToken>('/api/auth/refresh', {}).pipe(
      tap(token => {
        this.isAuthenticated.set(true);
        if (token.athlete) {
          this.currentAthlete.set(token.athlete);
        }
      })
    );
  }

  logout(): void {
    this.cache.clearAll(); // Clear cache on logout
    this.isAuthenticated.set(false);
    this.currentAthlete.set(null);
  }

  getActivities(page = 1, perPage = 30): Observable<StravaActivity[]> {
    const cacheKey = `activities_${page}_${perPage}`;
    return this.cache.getOrFetch(
      cacheKey,
      () => this.api.get<StravaActivity[]>(`/api/activities?page=${page}&per_page=${perPage}`)
    );
  }

  getActivity(id: number): Observable<StravaActivity> {
    const cacheKey = `activity_${id}`;
    return this.cache.getOrFetch(
      cacheKey,
      () => this.api.get<StravaActivity>(`/api/activities/${id}`)
    );
  }

  getActivityDetail(id: number): Observable<ActivityDetail> {
    const cacheKey = `activity_detail_${id}`;
    return this.cache.getOrFetch(
      cacheKey,
      () => this.api.get<ActivityDetail>(`/api/activities/${id}`)
    );
  }

  getActivityLaps(id: number): Observable<Lap[]> {
    const cacheKey = `activity_laps_${id}`;
    return this.cache.getOrFetch(
      cacheKey,
      () => this.api.get<Lap[]>(`/api/activities/${id}/laps`)
    );
  }

  getAthleteStats(athleteId: number): Observable<AthleteStats> {
    const cacheKey = `athlete_stats_${athleteId}`;
    return this.cache.getOrFetch(
      cacheKey,
      () => this.api.get<AthleteStats>(`/api/stats/${athleteId}`)
    );
  }

  getAthlete(): Observable<StravaAthlete> {
    const cacheKey = 'athlete_profile';
    return this.cache.getOrFetch(
      cacheKey,
      () => this.api.get<StravaAthlete>('/api/athlete')
    );
  }

  /**
   * Force refresh data by clearing cache for a specific pattern
   */
  refreshActivities(): void {
    this.cache.invalidatePattern('activities');
  }

  refreshActivity(id: number): void {
    this.cache.remove(`activity_${id}`);
    this.cache.remove(`activity_detail_${id}`);
    this.cache.remove(`activity_laps_${id}`);
  }
}
