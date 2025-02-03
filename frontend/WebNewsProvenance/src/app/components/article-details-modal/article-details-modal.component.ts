import { Component, Inject, OnInit, Renderer2 } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ArticleService } from '../../services/article.service';
import {DOCUMENT} from "@angular/common";

@Component({
  selector: 'app-article-details-modal',
  templateUrl: './article-details-modal.component.html',
  styleUrls: ['./article-details-modal.component.scss']
})
export class ArticleDetailsModalComponent implements OnInit {
  articleData: any;

  constructor(
    private articleService: ArticleService,
    @Inject(MAT_DIALOG_DATA) public data: any,
    public dialogRef: MatDialogRef<ArticleDetailsModalComponent>,
    private renderer: Renderer2,
    @Inject(DOCUMENT) private document: Document,
  ) {}

  addJsonLdForArticle(articleData: any): void {
    const script = this.renderer.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify({
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
    });
    this.renderer.appendChild(this.document.head, script);
  }

  ngOnInit(): void {
    console.log('URL primit pentru articol:', this.data.article.url);
    console.log(this.data.article);


    if (this.data.article.url) {
      this.articleService.getArticleByUrl(this.data.article.url).subscribe({
        next: (response) => {
          console.log('Datele articolului primite:', response);

          this.articleData = response.data;
          if (this.articleData?.articleBody) {
            this.articleData.articleBody = this.articleData.articleBody.split('\n\n');
          }
          this.addJsonLdForArticle(this.articleData);
        },
        error: (error) => {
          console.error('Eroare la obținerea articolului:', error);
        }
      });
    }

  }
}
