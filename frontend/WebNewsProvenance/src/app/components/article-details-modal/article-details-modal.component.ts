import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ArticleService } from '../../services/article.service';

@Component({
  selector: 'app-article-details-modal',
  templateUrl: './article-details-modal.component.html',
  styleUrls: ['./article-details-modal.component.scss']
})
export class ArticleDetailsModalComponent implements OnInit {
  articleData: any;

  constructor(
    private articleService: ArticleService, // Injectează serviciul
    @Inject(MAT_DIALOG_DATA) public data: any,
    public dialogRef: MatDialogRef<ArticleDetailsModalComponent>
  ) {}

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
        },
        error: (error) => {
          console.error('Eroare la obținerea articolului:', error);
        }
      });
    }
  }
}
