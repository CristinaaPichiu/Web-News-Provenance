import { Component, OnInit, ViewChild, ElementRef, Input } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { forkJoin } from 'rxjs';

interface Article {
  headline: string;
  abstract: string;
  datePublished: string;
  url: string;
  thumbnailUrl: string;
  keywords: string[];
  author?: string;
  isFavorite?: boolean;
}

@Component({
  selector: 'app-history-card',
  templateUrl: './history-card.component.html',
  styleUrls: ['./history-card.component.scss']
})

export class HistoryCardComponent implements OnInit {
  @Input() articles: Article[] = [];
  currentIndex: number = 0;
  favoriteUrls: Set<string> = new Set();
  historyApiUrl: string = 'http://127.0.0.1:5000/user/history';
  favoritesApiUrl: string = 'http://127.0.0.1:5000/user/favorites';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchHistoryAndFavorites();
  }



  fetchHistoryAndFavorites(): void {
    const jwtToken = localStorage.getItem('access_token');

    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);

    // Use forkJoin to fetch both history and favorites simultaneously
    forkJoin({
      history: this.http.get<any>(this.historyApiUrl, { headers }),
      favorites: this.http.get<any>(this.favoritesApiUrl, { headers })
    }).subscribe({
      next: ({ history, favorites }) => {
        // Create set of favorite URLs
        this.favoriteUrls = new Set(favorites.data.map((item: any) => item.url));

        // Process history with favorite status
        if (history.message === 'Success') {
          this.articles = history.data.map((item: any) => ({
            headline: item.headline,
            abstract: item.abstract,
            datePublished: item.datePublished,
            url: item.url,
            thumbnailUrl: item.thumbnailUrl || 'https://via.placeholder.com/150',
            keywords: item.keywords,
            author: item.author[0]?.name,
            isFavorite: this.favoriteUrls.has(item.url)
          }));
        }
      },
      error: error => {
        console.error('Error fetching data:', error);
      }
    });
  }

  toggleFavorite(article: Article): void {
    const jwtToken = localStorage.getItem('access_token');
    if (!jwtToken) return;

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);
    const body = { url: article.url };

    if (article.isFavorite) {
      // If already favorited, remove from favorites
      this.http.delete(this.favoritesApiUrl, { headers, body }).subscribe({
        next: () => {
          article.isFavorite = false;
          this.favoriteUrls.delete(article.url);
        },
        error: error => {
          console.error('Error removing favorite:', error);
        }
      });
    } else {
      // If not favorited, add to favorites
      this.http.post(this.favoritesApiUrl, body, { headers }).subscribe({
        next: () => {
          article.isFavorite = true;
          this.favoriteUrls.add(article.url);
        },
        error: error => {
          console.error('Error adding favorite:', error);
        }
      });
    }
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
