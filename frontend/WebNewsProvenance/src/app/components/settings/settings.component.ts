import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

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
    private router: Router
  ) {}


  ngOnInit(): void {
    this.initializeForms();
    this.loadUserProfile();
    this.loadUserDetails();
    
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

  
  onChangePassword(): void {
   
  }
  
}
