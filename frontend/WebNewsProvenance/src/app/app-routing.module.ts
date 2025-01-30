import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import {SettingsComponent} from "./components/settings/settings.component";
import { ForgetPasswordComponent } from './components/forget-password/forget-password.component';
import { SetPasswordComponent } from './components/set-password/set-password.component';


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
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
