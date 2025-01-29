import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-forget-password',
  templateUrl: './forget-password.component.html',
  styleUrls: ['./forget-password.component.scss']
})
export class ForgetPasswordComponent {

  constructor(private router: Router) {}

  goBack() {
    this.router.navigate(['/login']); // Navighează înapoi la pagina de login sau oricare altă pagină
  }

}
