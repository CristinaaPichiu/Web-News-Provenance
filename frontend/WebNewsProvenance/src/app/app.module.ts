import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';


import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { LoginComponent } from './components/login/login.component';
import { ReactiveFormsModule } from '@angular/forms';
import { RegisterComponent } from './components/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { MatTabsModule } from '@angular/material/tabs';
import { SettingsComponent } from './components/settings/settings.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatList } from '@angular/material/list';
import { MatListModule } from '@angular/material/list';
import { ForgetPasswordComponent } from './components/forget-password/forget-password.component';
import { SetPasswordComponent } from './components/set-password/set-password.component';
import { ShowUsersComponent } from './components/show-users/show-users.component';
import { UserCardComponent } from './components/user-card/user-card.component';
import { EditUserDialogComponent } from './components/edit-user-dialog/edit-user-dialog.component';
import { DeleteUserDialogComponent } from './components/delete-user-dialog/delete-user-dialog.component';
import { CreateArticleComponent } from './components/create-article/create-article.component';
import { HistoryCardComponent } from './components/history-card/history-card.component';
import {MatChipsModule} from "@angular/material/chips";
import { MatStepperModule } from '@angular/material/stepper';
import { RecommendedArticlesComponent } from './components/recommended-articles/recommended-articles.component';
import { GraphVisualizationComponent } from './components/graph-visualization/graph-visualization.component';
import { FormsModule } from '@angular/forms';
import { SearchArticleComponent } from './components/search-article/search-article.component';
import { ArticleDetailsModalComponent } from './components/article-details-modal/article-details-modal.component';
import { FavoriteArticlesComponent } from './components/favorite-articles/favorite-articles.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    RegisterComponent,
    DashboardComponent,
    SettingsComponent,
    SidebarComponent,
    ForgetPasswordComponent,
    SetPasswordComponent,
    ShowUsersComponent,
    UserCardComponent,
    EditUserDialogComponent,
    DeleteUserDialogComponent,
    CreateArticleComponent,
    HistoryCardComponent,
    RecommendedArticlesComponent,
    GraphVisualizationComponent,
    SearchArticleComponent,
    ArticleDetailsModalComponent,
    FavoriteArticlesComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    ReactiveFormsModule,
    BrowserAnimationsModule,
    MatTabsModule,
    MatSidenavModule,
    MatListModule,
    AppRoutingModule,
    HttpClientModule,
    MatCardModule,
    MatDialogModule,
    MatChipsModule,
    MatStepperModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
