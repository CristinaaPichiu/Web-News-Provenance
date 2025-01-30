import { Component, Inject, Renderer2, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  hidePassword = true;
  hideConfirmPassword = true;
  passwordPattern = '^(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,}$';
  registerForm!: FormGroup;
  errorMessage: string = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService, // Injectează AuthService
    private router: Router,
    @Inject(DOCUMENT) private document: Document,
    private renderer: Renderer2
  ) { }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.pattern(this.passwordPattern)]],
      confirmPassword: ['', [Validators.required]]
    });
    this.addJsonLd();

  }

  checkPasswords(group: FormGroup): any {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    console.log("Password Check: ", password, confirmPassword);
    return password === confirmPassword ? null : { notSame: true };
  }

  togglePasswordVisibility(): void {
    this.hidePassword = !this.hidePassword;
  }

  toggleConfirmPasswordVisibility(): void {
    this.hideConfirmPassword = !this.hideConfirmPassword;
  }

  onRegister(): void {
    if (this.registerForm.valid && !this.registerForm.hasError('notSame')) {
      const { first_name, last_name, email, password } = this.registerForm.value;
      this.authService.register(first_name, last_name, email, password).subscribe({
        next: () => {
          this.router.navigate(['/dashboard']); // Redirecționează după înregistrare
          console.log('Registration successful');
        },
        error: (error: Error) => {
          this.errorMessage = error.message;
          console.log('Registration failed:', this.errorMessage);
        }
      });
    } else {
      this.errorMessage = 'Please check your registration details and try again.';
    }
  }

  addJsonLd() {
    const script = this.renderer.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Login Page",
      "description": "Login to your account",
      "image": { "@type": "ImageObject", "url": "https://github.com/CristinaaPichiu/Web-News-Provenance/blob/main/frontend/WebNewsProvenance/src/assets/registerBun.png" },
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
        "name": "Register Form",
        "cssSelector": ".register-container",
        "description": "A registration form that allows users to create a new account."
      },
      "potentialAction": {
        "@type": "RegisterAction",
        "target": "https://yourcompany.com/api/register",
        "name": "User Registration",
        "description": "Allows a new user to create an account.",
        "input": [
          {
            "@type": "PropertyValue",
            "name": "First Name",
            "valueRequired": true
          },
          {
            "@type": "PropertyValue",
            "name": "Last Name",
            "valueRequired": true
          },
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
