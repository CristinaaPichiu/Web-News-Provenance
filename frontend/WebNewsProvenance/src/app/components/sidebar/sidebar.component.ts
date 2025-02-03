import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {

  isSmallScreen = false;
  role: string = '';


  constructor(private breakpointObserver: BreakpointObserver, private authService: AuthService) {}

  logout(): void {
    localStorage.removeItem('access_token');
  }

  ngOnInit() {
    this.breakpointObserver.observe([
      Breakpoints.XSmall,
      Breakpoints.Small
    ]).subscribe(result => {
      this.isSmallScreen = result.matches;
    });

    this.authService.getRole().subscribe(role => {
      this.role = role;
    });

    this.authService.loadUserRole();

  }

}
