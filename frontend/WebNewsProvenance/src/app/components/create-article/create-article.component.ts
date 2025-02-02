import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ArticleService } from 'src/app/services/article.service';
import { tap } from 'rxjs/operators';

@Component({
  selector: 'app-create-article',
  templateUrl: './create-article.component.html',
  styleUrls: ['./create-article.component.scss']
})
export class CreateArticleComponent {
  articleForm: FormGroup;
  responseData: any = null;
  errorMessage: string | null = null;
  isLoading = false; // Adăugat pentru loader

  constructor(private fb: FormBuilder, private articleService: ArticleService) {
    this.articleForm = this.fb.group({
      url: ['', [
        Validators.required,
        Validators.pattern('https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)')
      ]]
    });
  }

  onSubmit() {
    if (this.articleForm.invalid) return;
  
    const url = this.articleForm.value.url;
    this.articleService.createArticle(url).subscribe(
      (data) => {
        this.responseData = this.filterNullValues(data);
        this.errorMessage = '';
      },
      (error) => {
        this.errorMessage = 'Eroare la trimiterea URL-ului.';
        this.responseData = null;
      }
    );
  }
  
  /** ✅ Funcție pentru eliminarea câmpurilor null */
  filterNullValues(obj: any): any {
    if (!obj || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) {
      return obj
        .map((item) => this.filterNullValues(item))
        .filter((item) => item !== null && item !== undefined);
    }
    return Object.fromEntries(
      Object.entries(obj)
        .filter(([_, value]) => value !== null && value !== undefined)
        .map(([key, value]) => [key, this.filterNullValues(value)])
    );
  }
  
}
