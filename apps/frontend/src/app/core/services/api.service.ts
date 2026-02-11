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

  private getCsrfToken(): string | null {
    const matches = document.cookie.match(/(?:^|; )strava_csrf=([^;]+)/);
    return matches ? decodeURIComponent(matches[1]) : null;
  }

  private buildOptions(options?: object, includeCsrf = false): object {
    const csrfToken = includeCsrf ? this.getCsrfToken() : null;
    const existingHeaders = (options as { headers?: HttpHeaders } | undefined)?.headers;
    let headers = existingHeaders ?? new HttpHeaders();

    if (csrfToken) {
      headers = headers.set('X-CSRF-Token', csrfToken);
    }

    return {
      withCredentials: true,
      ...options,
      headers
    };
  }

  get<T>(endpoint: string, options?: object): Observable<T> {
    const requestOptions = this.buildOptions(options);
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, requestOptions).pipe(
      retry(1),
      catchError(this.handleError)
    );
  }

  post<T>(endpoint: string, body: unknown, options?: object): Observable<T> {
    const requestOptions = this.buildOptions(options, true);
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, body, requestOptions).pipe(
      catchError(this.handleError)
    );
  }

  put<T>(endpoint: string, body: unknown, options?: object): Observable<T> {
    const requestOptions = this.buildOptions(options, true);
    return this.http.put<T>(`${this.baseUrl}${endpoint}`, body, requestOptions).pipe(
      catchError(this.handleError)
    );
  }

  delete<T>(endpoint: string, options?: object): Observable<T> {
    const requestOptions = this.buildOptions(options, true);
    return this.http.delete<T>(`${this.baseUrl}${endpoint}`, requestOptions).pipe(
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
