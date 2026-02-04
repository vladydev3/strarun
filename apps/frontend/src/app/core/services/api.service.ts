import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('strava_token');
    if (token) {
      const tokenData = JSON.parse(token);
      return new HttpHeaders({
        'Authorization': `Bearer ${tokenData.access_token}`
      });
    }
    return new HttpHeaders();
  }

  get<T>(endpoint: string, options?: object): Observable<T> {
    const headers = this.getAuthHeaders();
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, { headers, ...options }).pipe(
      retry(1),
      catchError(this.handleError)
    );
  }

  post<T>(endpoint: string, body: unknown, options?: object): Observable<T> {
    const headers = this.getAuthHeaders();
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, body, { headers, ...options }).pipe(
      catchError(this.handleError)
    );
  }

  put<T>(endpoint: string, body: unknown, options?: object): Observable<T> {
    const headers = this.getAuthHeaders();
    return this.http.put<T>(`${this.baseUrl}${endpoint}`, body, { headers, ...options }).pipe(
      catchError(this.handleError)
    );
  }

  delete<T>(endpoint: string, options?: object): Observable<T> {
    const headers = this.getAuthHeaders();
    return this.http.delete<T>(`${this.baseUrl}${endpoint}`, { headers, ...options }).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }

    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
