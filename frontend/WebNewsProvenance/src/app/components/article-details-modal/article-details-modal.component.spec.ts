import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArticleDetailsModalComponent } from './article-details-modal.component';

describe('ArticleDetailsModalComponent', () => {
  let component: ArticleDetailsModalComponent;
  let fixture: ComponentFixture<ArticleDetailsModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ArticleDetailsModalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArticleDetailsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
