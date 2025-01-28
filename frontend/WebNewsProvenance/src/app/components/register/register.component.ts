import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';


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
    private router: Router
  ) { }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.pattern(this.passwordPattern)]],
      confirmPassword: ['', [Validators.required]]
    });
    
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
}
