import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-edit-user-dialog',
  templateUrl: './edit-user-dialog.component.html',
  styleUrls: ['./edit-user-dialog.component.scss']
})
export class EditUserDialogComponent {
  editUserForm: FormGroup;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private userService: AuthService,
    public dialogRef: MatDialogRef<EditUserDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.editUserForm = this.fb.group({
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onSubmit(): void {
    if (this.editUserForm.valid) {
      this.isLoading = true;
      this.userService.updateUser(this.data.user.id, { password: this.editUserForm.value.password })
        .subscribe(
          response => {
            this.isLoading = false;
            this.dialogRef.close(true); 
          },
          error => {
            console.error('Error updating user password:', error);
            this.isLoading = false;
          }
        );
    }
  }
}
