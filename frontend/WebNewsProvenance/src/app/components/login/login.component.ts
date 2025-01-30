import { Component, Inject, Renderer2, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { DOCUMENT } from '@angular/common';

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
    private router: Router,
    @Inject(DOCUMENT) private document: Document,
    private renderer: Renderer2
  ) {}

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]    });
    this.addJsonLd();
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

  addJsonLd() {
    const script = this.renderer.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Login Page",
      "description": "Login to your account",
      "image": { "@type": "ImageObject", "url": "https://github.com/CristinaaPichiu/Web-News-Provenance/blob/main/frontend/WebNewsProvenance/src/assets/loginBun.png" },
      "author": [
        {
          "@type": "Person",
          "name": "Pichiu Cristina-Cătălina",
          "url": "https://github.com/CristinaaPichiu"
        },
        {
          "@type": "Person",
          "name": "Curduman Miruna-Diana",
          "url": "https://github.com/curduman-miruna/"
        }
      ],
      "hasPart": {
        "@type": "WebPageElement",
        "name": "Login Form",
        "cssSelector": ".login-container",
        "description": "A login form that allows users to enter their credentials."
      },
      "potentialAction": {
        "@type": "LoginAction",
        "target": "https://yourcompany.com/api/login",
        "name": "User Login",
        "description": "Allows a registered user to log into their account.",
        "input": [
          {
            "@type": "PropertyValue",
            "name": "Email",
            "valueRequired": true
          },
          {
            "@type": "PropertyValue",
            "name": "Password",
            "valueRequired": true
          }
        ]
      }
    });
    this.renderer.appendChild(this.document.head, script);
  }



}
