import { Component, OnInit, ViewChild, ElementRef, Input } from '@angular/core';
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
  selector: 'app-history-card',
  templateUrl: './history-card.component.html',
  styleUrls: ['./history-card.component.scss']
})

export class HistoryCardComponent implements OnInit {
  @Input() articles: Article[] = [];
  currentIndex: number = 0;
  historyApiUrl: string = 'http://127.0.0.1:5000/user/history';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchHistory();
  }

  fetchHistory(): void {
    const jwtToken = localStorage.getItem('access_token');

    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);
    const historyUrl = `${this.historyApiUrl}`;

    this.http.get<any>(historyUrl, { headers }).subscribe({
      next: historyResponse => {
        console.log('History Response:', historyResponse);
        if (historyResponse.message === 'Success') {
          this.articles = historyResponse.data.map((item: any) => ({
            headline: item.headline,
            abstract: item.abstract,
            datePublished: item.datePublished,
            url: item.url,
            thumbnailUrl: item.thumbnailUrl || 'https://via.placeholder.com/150',
            keywords: item.keywords,
            author: item.author[0]?.name
          }));
          console.log('Articles:', this.articles);
        }
      },
      error: error => {
        console.error('Error fetching history:', error);
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
