// src/app/services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = 'http://localhost:5000/auth'; // Actualizează cu URL-ul serverului tău

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/login`, { email, password }).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
      }),
      catchError(error => {
        let message = "Login failed. Please check your credentials.";
        if (error.error instanceof ErrorEvent) {
          message = "An unexpected error occurred.";
        } else if (error.status === 401) {
          message = "Invalid email or password";
        } else if (error.error?.message) {
          message = error.error.message;
        }
        return throwError(() => new Error(message));
      })
    );
  }

  // Adaugă această metodă în serviciul AuthService

register(first_name: string, last_name: string, email: string, password: string): Observable<any> {
  return this.http.post<any>(`${this.baseUrl}/register`, { first_name, last_name, email, password }).pipe(
    tap(response => {
      localStorage.setItem('access_token', response.access_token); // Salvează token-ul dacă înregistrarea este direct urmată de autentificare
    }),
    catchError(error => {
      let message = "Registration failed. Please check your details.";
      if (error.error instanceof ErrorEvent) {
        message = "An unexpected error occurred.";
      } else if (error.status === 409) {
        message = "Email already in use";
      } else if (error.error?.message) {
        message = error.error.message;
      }
      return throwError(() => new Error(message));
    })
  );
}


  // Metode suplimentare pentru logout, refresh token etc.
}
