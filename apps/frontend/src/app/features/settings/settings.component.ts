import { Component, signal, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StravaService, StravaAthlete } from '../../core/services/strava.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss'
})
export class SettingsComponent implements OnInit {
  private stravaService = inject(StravaService);

  isConnected = signal(false);
  loading = signal(true);
  profile = signal<StravaAthlete | null>(null);
  
  settings = signal({
    syncFrequency: '1h',
    showPrivateActivities: false,
    distanceUnit: 'km',
    paceUnit: 'min/km'
  });

  ngOnInit() {
    this.checkConnection();
  }

  checkConnection() {
    this.loading.set(true);
    const isAuth = this.stravaService.isAuthenticated();
    this.isConnected.set(isAuth);
    
    if (isAuth) {
      const athlete = this.stravaService.currentAthlete();
      this.profile.set(athlete);
    } else {
      this.profile.set(null);
    }
    
    this.loading.set(false);
  }

  connectStrava() {
    window.location.href = this.stravaService.getAuthUrl();
  }

  disconnectStrava() {
    this.stravaService.logout();
    this.isConnected.set(false);
    this.profile.set(null);
  }

  syncNow() {
    // TODO: Trigger manual sync
    alert('Syncing activities...');
  }

  saveSettings() {
    // TODO: Save settings to API
    alert('Settings saved!');
  }
}
