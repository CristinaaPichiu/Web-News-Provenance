import { Component, Inject,ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Renderer2 } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
  passwordForm!: FormGroup;
  saveSuccess: boolean = false;

  @ViewChild('fileInput') fileInput!: ElementRef;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private renderer: Renderer2,
    @Inject(DOCUMENT) private document: Document
  ) {}


  ngOnInit(): void {
    this.initializeForms();
    this.loadUserProfile();
    this.loadUserDetails();
    this.addJsonLd();

  }
  loadUserDetails(): void {
    const token = localStorage.getItem('auth_token');
    if (token) {

    } else {
      console.error('Token de autorizare lipsă sau expirat.');
    }
  }

  loadUserProfile(): void {
    const token = localStorage.getItem('auth_token');

    if (token) {

    } else {
      console.error('Nu s-a găsit niciun token de autorizare. Utilizatorul trebuie să se autentifice.');
    }
  }

  initializeForms(): void {

    this.passwordForm = this.fb.group({
      currentPassword: ['', [Validators.required, Validators.minLength(6)]],
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmNewPassword: ['', [Validators.required]]
    }, {
      validator: this.mustMatch('newPassword', 'confirmNewPassword')
    });
  }
  mustMatch(passwordField: string, confirmPasswordField: string) {
    return (formGroup: FormGroup) => {
      const password = formGroup.controls[passwordField];
      const confirmPassword = formGroup.controls[confirmPasswordField];

      if (confirmPassword.errors && !confirmPassword.errors['mustMatch']) {
        return;
      }

      if (password.value !== confirmPassword.value) {
        confirmPassword.setErrors({ mustMatch: true });
      } else {
        confirmPassword.setErrors(null);
      }
    }
  }



  triggerFileInput(): void {
    this.fileInput.nativeElement.click();
  }

  addJsonLd() {
    const script = this.renderer.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Settings Page",
      "description": "User settings and password change",
      "image": { "@type": "ImageObject", "url": "https://github.com/CristinaaPichiu/Web-News-Provenance/blob/main/frontend/WebNewsProvenance/src/assets/forgot_password.png" },
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
        "name": "Settings Form",
        "cssSelector": ".settings-container",
        "description": "A form that allows users to change their password."
      },
      "potentialAction": {
        "@type": "UpdateAction",
        "target": "https://yourcompany.com/api/update-password",
        "name": "Password Update",
        "description": "Allows a user to update their password.",
        "input": [
          {
            "@type": "PropertyValue",
            "name": "Current Password",
            "valueRequired": true
          },
          {
            "@type": "PropertyValue",
            "name": "New Password",
            "valueRequired": true
          },
          {
            "@type": "PropertyValue",
            "name": "Confirm New Password",
            "valueRequired": true
          }
        ]
      }
    });
    this.renderer.appendChild(this.document.head, script);
  }

  onChangePassword(): void {

  }



}
