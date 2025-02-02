import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface Article {
  headline: string;
  abstract: string;
  datePublished: string;
  url: string;
  thumbnailUrl: string;
  keywords: string[];
  author?: string;
}

@Component({
  selector: 'app-recommended-articles',
  templateUrl: './recommended-articles.component.html',
  styleUrls: ['./recommended-articles.component.scss']
})
export class RecommendedArticlesComponent implements OnInit {
  articles: Article[] = []; // Initialize articles array
  currentIndex: number = 0; // Initialize
  recommendedApiUrl: string = 'http://127.0.0.1:5000/user/recommend';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchRecommended();
  }

  fetchRecommended(): void {
    const jwtToken = localStorage.getItem('access_token');

    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);
    const historyUrl = `${this.recommendedApiUrl}`;

    this.http.get<any>(historyUrl, { headers }).subscribe({
      next: recommendedResponse => {
        console.log('Recommended Response:', recommendedResponse);
        if (recommendedResponse.message === 'Success') {
          this.articles = recommendedResponse.recommended_articles.map((item: any) => ({
            headline: item.headline,
            abstract: item.abstract,
            datePublished: item.datePublished,
            url: item.url,
            thumbnailUrl: item.thumbnailUrl || 'https://via.placeholder.com/150',
            keywords: item.keywords,
            author: item.author[0]?.name
          }));
          console.log('Recommended Articles:', this.articles);
        }
      },
      error: error => {
        console.error('Error fetching recommended articles.', error);
      }
    });
  }

  next() {
    if (this.currentIndex < this.maxIndex) {
      this.currentIndex++;
    }
  }

  previous() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
    }
  }

  get maxIndex(): number {
    return Math.max(0, this.articles.length - 3); // Show 3 articles per page
  }

  get transform(): string {
    return `translateX(${this.currentIndex * -33.33}%)`; // 33.33% per card to show 3 per page
  }
}
