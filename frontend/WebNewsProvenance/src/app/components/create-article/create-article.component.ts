import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ArticleService } from 'src/app/services/article.service';
import { tap } from 'rxjs/operators';

@Component({
  selector: 'app-create-article',
  templateUrl: './create-article.component.html',
  styleUrls: ['./create-article.component.scss']
})
export class CreateArticleComponent implements OnInit {
  articleForm: FormGroup;
  responseData: any = null;
  errorMessage: string | null = null;
  isLoading = false;
  jsonLd: any;

  generateJsonLd(articleData: any): void {
    this.jsonLd = {
      "@context": "https://schema.org",
      "@type": articleData['@type'],
      "dataCreated": articleData.dataCreated,
      "dateModified": articleData.dateModified,
      "url": articleData.url,
      "publisher": articleData.publisher.map((publisher: any) => ({
        "@type": "Organization",
        "name": publisher.name,
      })),
      'thumbnailUrl': articleData.thumbnailUrl,
      'wordCount': articleData.wordCount,
      "headline": articleData.headline,
      "author": articleData.author.map((author: any) => ({
        "@type": "Person",
        "name": author.name
      })),
      "datePublished": articleData.datePublished,
      "abstract": articleData.abstract,
      "articleBody": articleData.articleBody.join('\n\n')
    };
  }

  generateJsonLdForPage(): void {
    this.jsonLd = {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Create Article Page",
      "url": window.location.href,
      "description": "Page to create and view articles"
    };
  }

  ngOnInit(): void {
    this.generateJsonLdForPage();
    this.addJsonLdToDocument();
  }

  constructor(private fb: FormBuilder, private articleService: ArticleService) {
    this.articleForm = this.fb.group({
      url: ['', [
        Validators.required,
        Validators.pattern('https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)')
      ]]
    });

  }

  addJsonLdToDocument(): void {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(this.jsonLd);
    document.head.appendChild(script);
  }

  onSubmit() {
    if (this.articleForm.invalid) return;

    const url = this.articleForm.value.url;
    this.articleService.createArticle(url).subscribe(
      (data) => {
        this.responseData = this.filterNullValues(data);
        this.errorMessage = '';
        this.generateJsonLd(this.responseData.data);
      },
      (error) => {
        this.errorMessage = 'Eroare la trimiterea URL-ului.';
        this.responseData = null;
      }
    );
  }

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
