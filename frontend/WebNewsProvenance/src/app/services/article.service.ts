import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ArticleService {
  private apiUrl = 'http://127.0.0.1:5000/article';
  private access_token = localStorage.getItem('access_token');
  constructor(private http: HttpClient) {}

  createArticle(url: string): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.access_token}`
    });

    return this.http.post<any>(`${this.apiUrl}/create`, { url }, { headers });
  }

  getArticleByUrl(url: string): Observable<any> {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.access_token}`
    });
    const params = new HttpParams().set('url', url);

    return this.http.get<any>(`${this.apiUrl}`, { headers, params });
  }
}
