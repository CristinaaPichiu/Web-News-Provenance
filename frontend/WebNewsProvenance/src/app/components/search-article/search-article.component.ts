import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SearchService } from 'src/app/services/search.service';
import { ArticleDetailsModalComponent } from '../article-details-modal/article-details-modal.component';
import { MatDialog } from '@angular/material/dialog';
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
  selector: 'app-search-article',
  templateUrl: './search-article.component.html',
  styleUrls: ['./search-article.component.scss']
})
export class SearchArticleComponent implements OnInit {
  searchForm!: FormGroup;
  showAdvancedSearch = false;
  searchResults: any[] = [];
  searchType: string = '';
  favoriteUrls: Set<string> = new Set();
  historyApiUrl: string = 'http://127.0.0.1:5000/user/history';
  favoritesApiUrl: string = 'http://127.0.0.1:5000/user/favorites';


  constructor(private fb: FormBuilder, private searchService: SearchService, private dialog: MatDialog, private http: HttpClient) {}

  ngOnInit() {
    this.initializeForm();
    this.fetchFavorites();
  }

  fetchFavorites(): void {
    const jwtToken = localStorage.getItem('access_token');

    if (!jwtToken) {
      console.error('User not authenticated');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${jwtToken}`);

    this.http.get<any>(this.favoritesApiUrl, { headers }).subscribe({
      next: (favorites) => {
        this.favoriteUrls = new Set(favorites.data.map((item: any) => item.url));
      },
      error: (error) => {
        console.error('Error fetching favorites:', error);
      }
    });
  }

  private initializeForm(): void {
    this.searchForm = this.fb.group({
      keywords: ['', [Validators.required, Validators.minLength(1)]],
      advancedSearch: this.fb.group({
        inLanguage: [''],
        author: [''],
        nationality: [''],
        publisher: [''],
        wordcount_min: ['', [Validators.min(0)]],
        wordcount_max: ['', [Validators.min(0)]],
        datePublished_min: [''],
        datePublished_max: ['']
      })
    });
  }

  toggleAdvancedSearch(): void {
    this.showAdvancedSearch = !this.showAdvancedSearch;
  }

  onSearch(): void {
    if (this.searchForm.valid) {
      const formValue = this.searchForm.value;
      const combinedSearch = {
        ...formValue.advancedSearch,
        keywords: formValue.keywords
      };

      if (this.showAdvancedSearch) {
        this.searchService.advancedSearch(combinedSearch).subscribe({
          next: (response) => {
            this.searchResults = Array.isArray(response.data) ? response.data.map((item: any) => ({
              ...item,
              isFavorite: this.favoriteUrls.has(item.url)
            })) : [];
            this.searchType = response.type;
            console.log('Advanced search results:', this.searchResults);
          },
          error: (error) => {
            console.error('Advanced search failed:', error);
            this.searchResults = [];
          }
        });
      } else {
        this.searchService.searchKeywords(formValue.keywords).subscribe({
          next: (response) => {
            this.searchResults = Array.isArray(response.data) ? response.data.map((item: any) => ({
              ...item,
              isFavorite: this.favoriteUrls.has(item.url)
            })) : [];
            this.searchType = response.type;
            console.log('Keyword search results:', response);
          },
          error: (error) => {
            console.error('Keyword search failed:', error);
            this.searchResults = [];
          }
        });
      }
    } else {
      this.markFormGroupTouched(this.searchForm);
    }
  }


  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.values(formGroup.controls).forEach(control => {
      control.markAsTouched();
      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }

  resetForm(): void {
    this.searchForm.reset();
    this.showAdvancedSearch = false;
    this.searchResults = [];
    this.searchType = '';
  }



  resetAdvancedSearch(): void {
    this.searchForm.get('advancedSearch')?.reset();
  }

  get searchTermControl() {
    return this.searchForm.get('keywords');
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


}
