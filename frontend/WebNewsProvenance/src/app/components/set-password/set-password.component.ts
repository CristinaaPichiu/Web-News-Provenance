import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-set-password',
  templateUrl: './set-password.component.html',
  styleUrls: ['./set-password.component.scss']
})
export class SetPasswordComponent implements OnInit {
  setPasswordForm!: FormGroup;
  errorMessage: string = '';
  hidePassword = true;
  hideConfirmPassword = true;
  token: string = ''; // Stocăm token-ul de resetare


  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute

  ) {}

  ngOnInit(): void {

    this.route.queryParams.subscribe(params => {
      this.token = params['token']; 
    });

    this.setPasswordForm = this.fb.group({
      password: ['', [Validators.required, Validators.minLength(8), this.passwordStrengthValidator.bind(this)]],
      confirmPassword: ['', Validators.required]
    }, { validator: this.passwordMatchValidator });
  }

  togglePasswordVisibility(): void {
    this.hidePassword = !this.hidePassword;
  }

  toggleConfirmPasswordVisibility(): void {
    this.hideConfirmPassword = !this.hideConfirmPassword;
  }

  passwordMatchValidator(g: FormGroup): { [key: string]: boolean } | null {
    const password = g.get('password')?.value;
    const confirmPassword = g.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { 'mismatch': true };
  }

  passwordStrengthValidator(control: AbstractControl): ValidationErrors | null {
    const value: string = control.value;
    let hasUpperCase = /[A-Z]+/.test(value);
    let hasLowerCase = /[a-z]+/.test(value);
    let hasNumeric = /[0-9]+/.test(value);
    let hasSpecial = /[\W]+/.test(value);

    const valid = hasUpperCase && hasLowerCase && hasNumeric && hasSpecial;
    return valid ? null : { 'passwordStrength': 'Password must have at least one uppercase, one lowercase, one number, and one special character' };
  }

  onSubmit(): void {
    if (this.setPasswordForm.invalid) {
      return;
    }

    const newPassword = this.setPasswordForm.value.password;
    
    this.authService.resetPassword(this.token, newPassword).subscribe({
      next: () => {
        this.router.navigate(['/login']); 
      },
      error: (error) => {
        this.errorMessage = error.error.message || 'An error occurred';
      }
    });
  }
}
