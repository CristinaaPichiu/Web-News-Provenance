import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private roleSource = new BehaviorSubject<string>('');
  public role = this.roleSource.asObservable();
  private baseUrl = 'http://localhost:5000/auth';

  private apiUrl = 'http://localhost:5000/email';
  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/login`, { email, password }).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        this.loadUserRole();
      })
    );
  }

  register(first_name: string, last_name: string, email: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/register`, { first_name, last_name, email, password }).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
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

  resetPassword(token: string, newPassword: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/reset-password/${token}`, { new_password: newPassword });
  }

  requestPasswordReset(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/request-reset-email`, { email });
  }


  loadUserRole() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<{ role: string }>(`${this.baseUrl}/get-user-role`, { headers }).subscribe(
      response => this.roleSource.next(response.role),
      error => console.error("Failed to load user role", error)
    );
  }

  getRole(): Observable<string> {
    return this.role;
  }

  getUsers(): Observable<any[]> {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    return this.http.get<any[]>(`${this.baseUrl}/get-users`, { headers });
  }

  updateUser(userId: string, userData: any): Observable<any> {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    return this.http.put(`${this.baseUrl}/update-user/${userId}`, userData, { headers });
  }

  deleteUser(userId: string): Observable<any> {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    return this.http.delete(`${this.baseUrl}/delete-user/${userId}`, { headers });
  }

  changePassword(currentPassword: string, newPassword: string): Observable<any> {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    const payload = { currentPassword, newPassword };

    return this.http.post(`${this.baseUrl}/change-password`, payload, { headers });
  }



}
