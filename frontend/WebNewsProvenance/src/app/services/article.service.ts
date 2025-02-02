import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ArticleService {
  private apiUrl = 'http://127.0.0.1:5000/article/create'; 

  constructor(private http: HttpClient) {}

  createArticle(url: string): Observable<any> {
    const token = localStorage.getItem('access_token'); 
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}` 
    });

    return this.http.post<any>(this.apiUrl, { url }, { headers });
  }
}
