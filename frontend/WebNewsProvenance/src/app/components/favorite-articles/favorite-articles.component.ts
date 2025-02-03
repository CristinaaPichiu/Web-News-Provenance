import {Component, OnInit, Inject, Renderer2} from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http'
import {DOCUMENT} from "@angular/common";
import {ArticleDetailsModalComponent} from "../article-details-modal/article-details-modal.component";
import {MatDialog} from "@angular/material/dialog";

interface Article {
  id: string;
  headline: string;
  abstract: string;
  datePublished: string;
  url: string;
  thumbnailUrl: string;
  keywords: string[];
  author?: string;
}

@Component({
  selector: 'app-favorite-articles',
  templateUrl: './favorite-articles.component.html',
  styleUrls: ['./favorite-articles.component.scss']
})
export class FavoriteArticlesComponent implements OnInit {
  jsonLd: any;
  articles: Article[] = [];
  currentPage: number = 1;
  itemsPerPage: number = 6;
  favoritesApiUrl: string = 'http://127.0.0.1:5000/user/favorites';


  constructor(private http: HttpClient, @Inject(DOCUMENT) private document: Document, private renderer: Renderer2, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.fetchFavorites();
    this.addJsonLdForArticles();
    this.addJsonLd();
  }

  addJsonLdForArticles(): void {
    const existingScripts = this.document.head.querySelectorAll('script[type="application/ld+json"]');
    existingScripts.forEach(script => this.renderer.removeChild(this.document.head, script));

    this.articles.forEach(article => {
      const script = this.renderer.createElement('script');
      script.type = 'application/ld+json';
      script.textContent = this.generateArticleJsonLd(article);
      this.renderer.appendChild(this.document.head, script);
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

  addJsonLd() {
    const script = this.renderer.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      "name": "Favorites Page",
      "description": "A list of your favorite articles",
      "author": [
        {
          "@type": "Person",
          "name": "Pichiu Cristina-Cătălina",
          "url": "https://github.com/CristinaaPichiu"
        },
        {
          "@type": "Person",
          "name": "Curduman Miruna-Diana",
          "url": "https://github.com/curduman-miruna/"
        }
      ],
      "hasPart": {
        "@type": "WebPageElement",
        "name": "Favorite Articles List",
        "cssSelector": ".favorites-container",
        "description": "A list of articles that the user has marked as favorite."
      }
    });
    this.renderer.appendChild(this.document.head, script);
  }

  fetchFavorites(): void {
    const jwtToken = localStorage.getItem('access_token');

    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);

    this.http.get<any>(this.favoritesApiUrl, { headers }).subscribe({
      next: response => {
        if (response.message === 'Success') {
          this.articles = response.data.map((item: any) => ({
            id: item.id,
            headline: item.headline,
            abstract: item.abstract,
            datePublished: item.datePublished,
            url: item.url,
            thumbnailUrl: item.thumbnailUrl || 'https://via.placeholder.com/150',
            keywords: item.keywords,
            author: item.author[0]?.name
          }));
          this.addJsonLdForArticles();
          if (this.currentPage > this.totalPages) {
            this.currentPage = Math.max(1, this.totalPages);
          }
        }
      },
      error: error => {
        if (error.status === 404) {
          this.articles = [];
        } else {
          console.error('Error fetching favorites:', error);
        }
      }
    });
  }

  removeFavorite(articleUrl: string): void {
    const jwtToken = localStorage.getItem('access_token');
    if (!jwtToken) return;

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);
    const body = { url: articleUrl };

    this.http.delete(this.favoritesApiUrl, { headers, body }).subscribe({
      next: () => {
        this.articles = this.articles.filter(article => article.url !== articleUrl);
        if (this.paginatedArticles.length === 0 && this.currentPage > 1) {
          this.currentPage--;
        }
      },
      error: error => {
        console.error('Error removing favorite:', error);
      }
    });
  }

  get totalPages(): number {
    return Math.ceil(this.articles.length / this.itemsPerPage);
  }

  get paginatedArticles(): Article[] {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    return this.articles.slice(startIndex, startIndex + this.itemsPerPage);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  openDialog(article: Article) {
    console.log("Search: " + article);
    const jwtToken = localStorage.getItem('access_token');
    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);
    this.http.post('http://127.0.0.1:5000/user/history', { url: article.url }, { headers }).subscribe({
      next: () => {
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

}
