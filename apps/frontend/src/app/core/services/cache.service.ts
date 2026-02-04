import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class CacheService {
  private readonly CACHE_PREFIX = 'strarun_cache_';
  private readonly DEFAULT_TTL = 60 * 60 * 1000; // 1 hour in milliseconds

  /**
   * Get data from cache if valid, otherwise execute the request and cache the result
   */
  getOrFetch<T>(
    key: string,
    fetchFn: () => Observable<T>,
    ttl: number = this.DEFAULT_TTL
  ): Observable<T> {
    const cached = this.get<T>(key);
    
    if (cached !== null) {
      return of(cached);
    }

    return fetchFn().pipe(
      tap(data => this.set(key, data, ttl))
    );
  }

  /**
   * Get data from cache
   */
  get<T>(key: string): T | null {
    try {
      const stored = localStorage.getItem(this.CACHE_PREFIX + key);
      if (!stored) return null;

      const entry: CacheEntry<T> = JSON.parse(stored);
      const now = Date.now();

      // Check if cache has expired
      if (now - entry.timestamp > this.DEFAULT_TTL) {
        this.remove(key);
        return null;
      }

      return entry.data;
    } catch {
      this.remove(key);
      return null;
    }
  }

  /**
   * Set data in cache
   */
  set<T>(key: string, data: T, ttl: number = this.DEFAULT_TTL): void {
    try {
      const entry: CacheEntry<T> = {
        data,
        timestamp: Date.now()
      };
      localStorage.setItem(this.CACHE_PREFIX + key, JSON.stringify(entry));
    } catch (e) {
      // Handle quota exceeded - clear old cache entries
      console.warn('Cache storage full, clearing old entries');
      this.clearExpired();
    }
  }

  /**
   * Remove a specific cache entry
   */
  remove(key: string): void {
    localStorage.removeItem(this.CACHE_PREFIX + key);
  }

  /**
   * Clear all cache entries
   */
  clearAll(): void {
    const keysToRemove: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.CACHE_PREFIX)) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key));
  }

  /**
   * Clear expired cache entries
   */
  clearExpired(): void {
    const now = Date.now();
    const keysToRemove: string[] = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.CACHE_PREFIX)) {
        try {
          const stored = localStorage.getItem(key);
          if (stored) {
            const entry: CacheEntry<unknown> = JSON.parse(stored);
            if (now - entry.timestamp > this.DEFAULT_TTL) {
              keysToRemove.push(key);
            }
          }
        } catch {
          keysToRemove.push(key);
        }
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key));
  }

  /**
   * Invalidate cache entries matching a pattern
   */
  invalidatePattern(pattern: string): void {
    const keysToRemove: string[] = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.CACHE_PREFIX) && key.includes(pattern)) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key));
  }
}
