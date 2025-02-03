import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  constructor(private http: HttpClient) {}

  searchKeywords(keywords: string): Observable<any> {
    const url = `http://127.0.0.1:5000/article/search?keywords=${encodeURIComponent(keywords)}`;
    return this.http.get(url);
  }
  advancedSearch(params: any): Observable<any> {
    let queryParams = new HttpParams();
    Object.keys(params).forEach(key => {
      if (params[key]) {
        queryParams = queryParams.append(key, params[key]);
      }
    });
    const url = `http://127.0.0.1:5000/article/search/advanced`;
    return this.http.get(url, { params: queryParams });
  }
}
