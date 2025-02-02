import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import {SettingsComponent} from "./components/settings/settings.component";
import { ForgetPasswordComponent } from './components/forget-password/forget-password.component';
import { SetPasswordComponent } from './components/set-password/set-password.component';
import { UserCardComponent } from './components/user-card/user-card.component';
import { ShowUsersComponent } from './components/show-users/show-users.component';
import { CreateArticleComponent } from './components/create-article/create-article.component';
import {GraphVisualizationComponent} from "./components/graph-visualization/graph-visualization.component";
import { SearchArticleComponent } from './components/search-article/search-article.component';


const routes: Routes = [
  {
    path:'login',
    component: LoginComponent
  },
  {
    path:'register',
    component: RegisterComponent
  },
  {
    path:'dashboard',
    component: DashboardComponent
  },
  {
    path:'sidebar',
    component: SidebarComponent
  },
  {
    path:'settings',
    component: SettingsComponent
  },
  {
    path:'forget-password',
    component: ForgetPasswordComponent
  },
  {
    path: 'set-password',
    component: SetPasswordComponent
  },
  {
    path: 'user-card',
    component: UserCardComponent
  },
  {
    path: 'show-users',
    component: ShowUsersComponent
  },
  {
    path: 'create-article',
    component: CreateArticleComponent
  },
  {
    path: 'graph-view',
    component: GraphVisualizationComponent
  },
  {
    path: 'search-article',
    component: SearchArticleComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
