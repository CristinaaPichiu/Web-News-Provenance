import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  hidePassword = true;
  hideConfirmPassword = true;


  togglePasswordVisibility(): void {
    this.hidePassword = !this.hidePassword;
  }

  toggleConfirmPasswordVisibility(): void {
    this.hideConfirmPassword = !this.hideConfirmPassword;
  }
  loginForm!: FormGroup;
  errorMessage: string = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]    });
  }

  onLogin(): void {
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.authService.login(email, password).subscribe({
        next: () => this.router.navigate(['/dashboard']), 
        error: (error: Error) => this.errorMessage = error.message
      });
    } else {
      this.errorMessage = 'Please fill in all required fields.';
    }
  }

  requestPasswordReset(): void {
    const email = this.loginForm.get('email')?.value;

    if (!email) {
      this.errorMessage = 'Please enter your email before resetting the password.';
      return;
    }

    this.authService.requestPasswordReset(email).subscribe({
      next: (response) => {
        console.log(response);
        this.router.navigate(['/forget-password']); 
      },
      error: (err) => {
        console.error('Error sending reset email', err);
        this.errorMessage = 'Failed to send reset email. Please try again.';
      }
    });
  }


  
}