import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-show-users',
  templateUrl: './show-users.component.html',
  styleUrls: ['./show-users.component.scss']
})
export class ShowUsersComponent implements OnInit {
  users: any[] = [];

  constructor(private userService: AuthService) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.userService.getUsers().subscribe(
      (data) => this.users = data,
      (error) => console.error('Error fetching users:', error)
    );
  }

  deleteUser(userId: string) {
  this.userService.deleteUser(userId).subscribe(() => {
    this.users = this.users.filter(user => user.id !== userId);
  }, error => {
    console.error('Error deleting user:', error);
  });
}

}
