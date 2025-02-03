import { Component, OnInit, ViewChild, ElementRef, Input, Inject, Renderer2 } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { forkJoin } from 'rxjs';
import { DOCUMENT } from "@angular/common";
import {MatDialog} from "@angular/material/dialog";
import {ArticleDetailsModalComponent} from "../article-details-modal/article-details-modal.component";

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
  selector: 'app-recommended-articles',
  templateUrl: './recommended-articles.component.html',
  styleUrls: ['./recommended-articles.component.scss']
})
export class RecommendedArticlesComponent implements OnInit {
  articles: Article[] = [];
  currentIndex: number = 0;
  favoriteUrls: Set<string> = new Set();
  recommendedApiUrl: string = 'http://127.0.0.1:5000/user/recommend';
  favoritesApiUrl: string = 'http://127.0.0.1:5000/user/favorites';

  constructor(private http: HttpClient, private dialog: MatDialog, @Inject(DOCUMENT) private document: Document, private renderer: Renderer2) {}

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

  ngOnInit(): void {
    this.fetchRecommended();
  }

  openDialog(article: any): void {
    console.log("Search: " + article);
    this.dialog.open(ArticleDetailsModalComponent, {
      width: '150vw',
      height: '85vh',
      data: { article: article }
    });
  }

  fetchRecommended(): void {
    const jwtToken = localStorage.getItem('access_token');

    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);

    forkJoin({
      recommended: this.http.get<any>(this.recommendedApiUrl, { headers }),
      favorites: this.http.get<any>(this.favoritesApiUrl, { headers })
    }).subscribe({
      next: ({ recommended, favorites }) => {
        this.favoriteUrls = new Set(favorites.data.map((item: any) => item.url));
        if (recommended.message === 'Success') {
          this.articles = recommended.recommended_articles.map((item: any) => ({
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
