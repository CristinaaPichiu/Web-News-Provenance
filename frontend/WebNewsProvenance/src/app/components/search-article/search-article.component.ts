import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SearchService } from 'src/app/services/search.service';
import { ArticleDetailsModalComponent } from '../article-details-modal/article-details-modal.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'app-search-article',
  templateUrl: './search-article.component.html',
  styleUrls: ['./search-article.component.scss']
})
export class SearchArticleComponent implements OnInit {
  searchForm!: FormGroup;
  showAdvancedSearch = false;
  searchResults: any[] = [];  // Stocăm rezultatele căutării aici
  searchType: string = '';  // Adaugă o nouă proprietate pentru a stoca tipul de căutare


  constructor(private fb: FormBuilder, private searchService: SearchService, private dialog: MatDialog) {}

  ngOnInit() {
    this.initializeForm();
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
      // Combinați cuvintele cheie cu căutarea avansată
      const combinedSearch = {
        ...formValue.advancedSearch,
        keywords: formValue.keywords // Include cuvintele cheie în parametrii de căutare avansată
      };
  
      if (this.showAdvancedSearch) {
        this.searchService.advancedSearch(combinedSearch).subscribe({
          next: (response) => {
            this.searchResults = Array.isArray(response.data) ? response.data : [];
            this.searchType = response.type;  // Stocăm type separat
            console.log('Advanced search results:', this.searchResults);
          },
          error: (error) => {
            console.error('Advanced search failed:', error);
            this.searchResults = [];
          }
        });
      } else {
        // Dacă căutarea avansată nu este activată, utilizează doar cuvintele cheie
        this.searchService.searchKeywords(formValue.keywords).subscribe({
          next: (response) => {
            this.searchResults = Array.isArray(response.data) ? response.data : [];
            this.searchType = response.type;  // Stocăm type separat
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
  openDialog(article: any): void {
    console.log("Search: " + article); // Verifică ce se trimite către dialog
    this.dialog.open(ArticleDetailsModalComponent, {
      width: '150vw', // 80% din lățimea ecranului
      height: '85vh',
            data: { article: article }
    });
  }
  

}
