import { Component, OnInit, ViewChild, ElementRef, Input, Inject, Renderer2 } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { forkJoin } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import {ArticleDetailsModalComponent} from "../article-details-modal/article-details-modal.component";
import { DOCUMENT} from "@angular/common";

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

  constructor(private http: HttpClient, private dialog: MatDialog, @Inject(DOCUMENT) private document: Document, private renderer: Renderer2) {}

  ngOnInit(): void {
    this.fetchHistoryAndFavorites();
    this.addJsonLdForArticles();
  }

  addJsonLdForArticles(): void {
    const head = this.document.head;
    if (!head) {
      console.error('Document head not found');
      return;
    }

    const existingScripts = head.querySelectorAll('script[type="application/ld+json"]');
    existingScripts.forEach(script => {
      console.log('Removing existing script:', script);
      this.renderer.removeChild(head, script);
    });

    this.articles.forEach(article => {
      const script = this.renderer.createElement('script');
      script.type = 'application/ld+json';
      script.textContent = this.generateArticleJsonLd(article);
      console.log('Inserting new script:', script);
      this.renderer.appendChild(head, script);
    });
  }

  generateArticleJsonLd(article: Article): string {
    const jsonLd = {
      "@context": "http://schema.org",
      "@type": "Article",
      "headline": article.headline,
      "author": {
        "@type": "Person",
        "name": article.author
      },
      "datePublished": article.datePublished,
      "url": article.url,
      "image": article.thumbnailUrl,
      "keywords": article.keywords,
      "abstract": article.abstract
    };

    return JSON.stringify(jsonLd);
  }

  openDialog(article: Article): void {
    console.log("Search: " + article);
    const jwtToken = localStorage.getItem('access_token');
    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);
    this.http.post('http://127.0.0.1:5000/user/history', { url: article.url }, { headers }).subscribe({
      next: () => {
        this.fetchHistoryAndFavorites(); // Update the history displayed
        this.dialog.open(ArticleDetailsModalComponent, {
          width: '150vw',
          height: '85vh',
          data: { article: article }
        });
      },
      error: error => {
        console.error('Error sending history request:', error);
      }
    });
  }

  fetchHistoryAndFavorites(): void {
    const jwtToken = localStorage.getItem('access_token');

    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);

    forkJoin({
      history: this.http.get<any>(this.historyApiUrl, { headers }),
      favorites: this.http.get<any>(this.favoritesApiUrl, { headers })
    }).subscribe({
      next: ({ history, favorites }) => {
        this.favoriteUrls = new Set(favorites.data.map((item: any) => item.url));

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
          this.addJsonLdForArticles();
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
    return Math.max(0, this.articles.length - 3);
  }

  get transform(): string {
    return `translateX(${this.currentIndex * -33.33}%)`;
  }
}
