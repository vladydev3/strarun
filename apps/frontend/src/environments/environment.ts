export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  csrfCookieName: 'strava_csrf',
  strava: {
    clientId: 'YOUR_STRAVA_CLIENT_ID',
    redirectUri: 'http://localhost:4200/auth/callback'
  }
};
