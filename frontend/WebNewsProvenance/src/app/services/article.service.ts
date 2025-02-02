import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ArticleService {
  private apiUrl = 'http://127.0.0.1:5000/article'; // URL-ul de bază al API-ului

  constructor(private http: HttpClient) {}

  createArticle(url: string): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return this.http.post<any>(`${this.apiUrl}/create`, { url }, { headers });
  }

  getArticleByUrl(url: string): Observable<any> {
    const params = new HttpParams().set('url', url); 

    return this.http.get<any>(`${this.apiUrl}`, { params });
    console.log("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
  }
}
