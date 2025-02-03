import { Component, OnInit, Inject,Renderer2 } from '@angular/core';
import { DOCUMENT } from '@angular/common';
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  jsonLd: any;

  ngOnInit(): void {
    this.generateJsonLdForPage();
    this.addJsonLdToDocument();
  }

  constructor(@Inject(DOCUMENT) private document: Document, private renderer: Renderer2) {}

  addJsonLdToDocument(): void {
    const script = this.renderer.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(this.jsonLd);
    this.renderer.appendChild(this.document.head, script);
  }

  generateJsonLdForPage(): void {
    this.jsonLd = {
      "@context": "http://schema.org",
      "@type": "WebPage",
      "name": "Dashboard",
      "description": "The dashboard page of the application.",
      "url": "http://localhost:4200/dashboard",
      "mainEntity": {
        "@type": "WebPage",
        "name": "Dashboard",
        "description": "The dashboard page of the application.",
        "url": "http://localhost:4200/dashboard"
      }
    };
  }
}
