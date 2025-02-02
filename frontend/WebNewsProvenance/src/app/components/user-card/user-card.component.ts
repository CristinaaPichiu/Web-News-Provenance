import { Component, Input, Output, EventEmitter } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { EditUserDialogComponent } from '../edit-user-dialog/edit-user-dialog.component';
import { DeleteUserDialogComponent } from '../delete-user-dialog/delete-user-dialog.component';

@Component({
  selector: 'app-user-card',
  templateUrl: './user-card.component.html',
  styleUrls: ['./user-card.component.scss']
})
export class UserCardComponent {
  @Input() user: any;
  @Output() edit = new EventEmitter<any>();
  @Output() delete = new EventEmitter<string>(); // Adăugat @Output pentru delete


  constructor(private dialog: MatDialog) {}

  openDeleteDialog(): void {
    const dialogRef = this.dialog.open(DeleteUserDialogComponent, {
      width: '400px',
      data: { user: this.user }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.delete.emit(this.user.id); // Emiterea evenimentului pentru ștergere
      }
    });
  }

  openEditDialog(): void {
    const dialogRef = this.dialog.open(EditUserDialogComponent, {
      width: '400px',
      data: { user: this.user }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.edit.emit({ id: this.user.id, password: result.password });
      }
    });
  }
}
