import { Component, ElementRef, OnInit, ViewChild, OnDestroy, Inject, Renderer2 } from '@angular/core';
import { DOCUMENT } from '@angular/common';
import { HttpClient } from '@angular/common/http';

interface RDFTriple {
  s: { type: string; value: string };
  p: { type: string; value: string };
  o: { type: string; value: string };
}

interface RDFNode {
  id: string;
  label: string;
  type: string;
  x: number;
  y: number;
  value?: string;
}

interface RDFLink {
  source: string;
  target: string;
  predicate: string;
}

@Component({
  selector: 'app-graph-visualization',
  templateUrl: './graph-visualization.component.html',
  styleUrls: ['./graph-visualization.component.scss']
})
export class GraphVisualizationComponent implements OnInit, OnDestroy {
  @ViewChild('svgContainer', { static: true }) svgContainer!: ElementRef<HTMLDivElement>;
  @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

  private width = 1200;
  private height = 800;
  private nodeRadius = 20;
  private svg: SVGSVGElement | null = null;
  private mainGroup: SVGGElement | null = null;

  private nodes: RDFNode[] = [];
  private links: RDFLink[] = [];
  private filteredNodes: RDFNode[] = [];
  private filteredLinks: RDFLink[] = [];

  availableNodeTypes: string[] = [];
  selectedNodeTypes: { [key: string]: boolean } = {};
  articles: RDFNode[] = [];
  selectedArticles: { [key: string]: boolean } = {};

  searchTerm: string = '';
  searchResults: RDFNode[] = [];

  private currentZoom = 1;
  private viewboxX = 0;
  private viewboxY = 0;
  private isPanning = false;
  private startPanX = 0;
  private startPanY = 0;

  private selectedNode: RDFNode | null = null;
  private isDragging = false;
  private dragStartX = 0;
  private dragStartY = 0;

  private highlightedNodeId: string | null = null;
  private defaultOpacity = '1';
  private fadedOpacity = '0.2';

  private boundMouseMove: (e: MouseEvent) => void;
  private boundMouseUp: (e: MouseEvent) => void;
  private boundWheel: (e: WheelEvent) => void;
  private boundContextMenu: (e: Event) => void;

  constructor(private http: HttpClient, private renderer: Renderer2, @Inject(DOCUMENT) private document: Document) {
    this.boundMouseMove = this.handleMouseMove.bind(this);
    this.boundMouseUp = this.handleMouseUp.bind(this);
    this.boundWheel = this.handleWheel.bind(this);
    this.boundContextMenu = (e: Event) => e.preventDefault();
  }

  addJsonLdForPageAndElements() {
    const jsonLd = {
      "@context": "http://schema.org",
      "@type": "WebPage",
      "name": "Graph Visualization",
      "mainEntity": {
        "@type": "WebPageElement",
        "name": "Graph Container",
        "cssSelector": ".graph"
      },
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "http://example.com/search?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    };

    const script = this.renderer.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(jsonLd);
    this.renderer.appendChild(this.document.head, script);
  }

  selectAllArticles() {
    this.articles.forEach(article => {
      this.selectedArticles[article.id] = true;
    });
    this.applyFilters();
  }

  clearAllArticles() {
    this.articles.forEach(article => {
      this.selectedArticles[article.id] = false;
    });
    this.applyFilters();
  }

  public applyFilters() {
    this.filteredNodes = this.nodes.filter(node =>
        this.selectedNodeTypes[node.type]
    );
    const filteredNodeIds = new Set(this.filteredNodes.map(node => node.id));
    this.filteredLinks = this.links.filter(link =>
        filteredNodeIds.has(link.source) && filteredNodeIds.has(link.target)
    );

    if (this.mainGroup) {
      while (this.mainGroup.firstChild) {
        this.mainGroup.removeChild(this.mainGroup.firstChild);
      }
    }
    this.createGraphElements();
    this.updateGraph();
  }

  ngOnInit() {
    console.log('Component initialized');
    this.initializeGraph();
    this.fetchData();
    this.addJsonLdForPageAndElements();
  }

  fetchData() {
    console.log('Fetching data');
    this.http.get<any>('http://127.0.0.1:5000/article/data').subscribe({
      next: (response) => {
        console.log('Data received:', response);
        const triples: RDFTriple[] = this.transformResponseToTriples(response);
        this.processRDFData(triples);
        this.createGraphElements();
        this.updateGraph();
      },
      error: (error) => {
        console.error('Failed to fetch data', error);
      }
    });
  }

  toggleAllFilters(): void {
    const allSelected = Object.values(this.selectedNodeTypes).every(value => value);
    for (const type in this.selectedNodeTypes) {
      if (this.selectedNodeTypes.hasOwnProperty(type)) {
        this.selectedNodeTypes[type] = !allSelected;
      }
    }
    this.applyFilters();
  }

  get allFiltersSelected(): boolean {
    return Object.values(this.selectedNodeTypes).every(value => value);
  }

  private transformResponseToTriples(response: any): RDFTriple[] {
    const triples: RDFTriple[] = [];

    if (!response || !response.data || typeof response.data !== 'object') {
      console.warn("Invalid response format");
      return [];
    }

    Object.values(response.data).forEach((value: any) => {
      if (Array.isArray(value) && value.length === 3) {
        const [subject, predicate, object] = value;

        if (typeof subject === 'string' && typeof predicate === 'string' && object !== undefined) {
          if (predicate === "http://schema.org/keywords" && Array.isArray(object)) {
            object.forEach((keyword) => {
              triples.push({
                s: { type: 'uri', value: subject },
                p: { type: 'uri', value: predicate },
                o: { type: 'literal', value: String(keyword) }
              });
            });
          } else {
            triples.push({
              s: { type: 'uri', value: subject },
              p: { type: 'uri', value: predicate },
              o: {
                type: this.isURI(object) ? 'uri' : 'literal',
                value: String(object)
              }
            });
          }
        } else {
          console.warn("Skipping malformed triple array:", value);
        }
      } else if (
          typeof value === 'object' &&
          value.s && value.p && value.o &&
          typeof value.s.value === 'string' &&
          typeof value.p.value === 'string' &&
          (typeof value.o.value === 'string' || Array.isArray(value.o.value))
      ) {
        if (value.p.value === "http://schema.org/keywords" && Array.isArray(value.o.value)) {
          value.o.value.forEach((keyword: string) => {
            triples.push({
              s: value.s,
              p: value.p,
              o: { type: 'literal', value: String(keyword) }
            });
          });
        } else {
          triples.push(value);
        }
      } else {
        console.warn("Skipping non-triple value:", value);
      }
    });

    return triples;
  }



  ngOnDestroy() {
    document.removeEventListener('mousemove', this.boundMouseMove);
    document.removeEventListener('mouseup', this.boundMouseUp);
    this.svg?.removeEventListener('wheel', this.boundWheel);
    this.svg?.removeEventListener('contextmenu', this.boundContextMenu);
  }

  private processRDFData(rdfTriples: RDFTriple[]) {
    const nodeMap = new Map<string, RDFNode>();
    this.links = [];
    this.nodes = [];
    const publisherRelations = new Set<string>();
    const authorRelations = new Set<string>();
    const headlineRelations = new Set<string>();
    const nameRelations = new Map<string, string>();
    const languageRelations = new Map<string, string>();
    const nationalityRelations = new Map<string, string>();
    const jobTitleRelations = new Map<string, string>();
    const sectionRelations = new Map<string, string>();

    rdfTriples.forEach(triple => {
      const predicate = triple.p.value.toLowerCase();

      if (predicate.includes('headline')) {
        headlineRelations.add(triple.s.value);
        if (!nodeMap.has(triple.s.value)) {
          nodeMap.set(triple.s.value, {
            id: triple.s.value,
            label: triple.o.value,
            type: 'Unknown',
            x: Math.random() * this.width,
            y: Math.random() * this.height,
            value: triple.o.value
          });
        } else {
          const node = nodeMap.get(triple.s.value);
          if (node) {
            node.label = triple.o.value;
            node.value = triple.o.value;
          }
        }
      }

      if (predicate.includes('inlanguage')) {
        const languageLabel = this.getLocalName(triple.o.value);
        const languageId = `lang_${languageLabel}`;

        nodeMap.set(languageId, {
          id: languageId,
          label: languageLabel,
          type: 'Language',
          x: Math.random() * this.width,
          y: Math.random() * this.height
        });

        this.links.push({
          source: triple.s.value,
          target: languageId,
          predicate: 'in language'
        });
      }


      if (predicate.includes('nationality')) {
        const nationalityId = `nationality_${triple.o.value}`;
        if (!nodeMap.has(nationalityId)) {
          nodeMap.set(nationalityId, {
            id: nationalityId,
            label: triple.o.value,
            type: 'Nationality',
            x: Math.random() * this.width,
            y: Math.random() * this.height
          });
        }
        this.links.push({
          source: triple.s.value,
          target: nationalityId,
          predicate: 'nationality'
        });
      }

      if (predicate.includes('jobtitle')) {
        const jobTitleId = `job_${triple.o.value}`;
        if (!nodeMap.has(jobTitleId)) {
          nodeMap.set(jobTitleId, {
            id: jobTitleId,
            label: triple.o.value,
            type: 'JobTitle',
            x: Math.random() * this.width,
            y: Math.random() * this.height
          });
        }
        this.links.push({
          source: triple.s.value,
          target: jobTitleId,
          predicate: 'job title'
        });
      }

      if (predicate.includes('articlesection')) {
        const sectionId = `section_${triple.o.value}`;
        if (!nodeMap.has(sectionId)) {
          nodeMap.set(sectionId, {
            id: sectionId,
            label: triple.o.value,
            type: 'Section',
            x: Math.random() * this.width,
            y: Math.random() * this.height
          });
        }
        this.links.push({
          source: triple.s.value,
          target: sectionId,
          predicate: 'section'
        });
      }

      if (predicate.includes('publisher')) {
        publisherRelations.add(triple.o.value);
        this.links.push({
          source: triple.s.value,
          target: triple.o.value,
          predicate: 'publisher'
        });
      }

      if (predicate.includes('author')) {
        authorRelations.add(triple.o.value);
        this.links.push({
          source: triple.s.value,
          target: triple.o.value,
          predicate: 'author'
        });
      }

      if (predicate.includes('name')) {
        nameRelations.set(triple.s.value, triple.o.value);
      }

      if (predicate.includes('keywords')) {
        const keywordId = `keyword_${triple.o.value}`;
        if (!nodeMap.has(keywordId)) {
          nodeMap.set(keywordId, {
            id: keywordId,
            label: triple.o.value,
            type: 'Keyword',
            x: Math.random() * this.width,
            y: Math.random() * this.height
          });
        }
        this.links.push({
          source: triple.s.value,
          target: keywordId,
          predicate: 'has keyword'
        });
      }

      if (!nodeMap.has(triple.s.value)) {
        nodeMap.set(triple.s.value, {
          id: triple.s.value,
          label: this.getDisplayLabel(triple.s.value),
          type: 'Unknown',
          x: Math.random() * this.width,
          y: Math.random() * this.height
        });
      }

      if (triple.o.type === 'uri' && !nodeMap.has(triple.o.value)) {
        nodeMap.set(triple.o.value, {
          id: triple.o.value,
          label: this.getDisplayLabel(triple.o.value),
          type: 'Unknown',
          x: Math.random() * this.width,
          y: Math.random() * this.height
        });
      }
    });

    nodeMap.forEach((node, id) => {
      if (headlineRelations.has(id)) {
        node.type = 'Article';
      }
      else if (publisherRelations.has(id) && nameRelations.has(id)) {
        node.type = 'Publisher';
        node.label = nameRelations.get(id) || node.label;
      }
      else if (authorRelations.has(id) && nameRelations.has(id)) {
        node.type = 'Author';
        node.label = nameRelations.get(id) || node.label;
      }
      else if (node.type === 'Unknown') {
        node.type = 'Resource';
      }
    });

    this.nodes = Array.from(nodeMap.values());

    this.availableNodeTypes = Array.from(new Set(this.nodes.map(node => node.type))).sort();
    this.availableNodeTypes.forEach(type => {
      this.selectedNodeTypes[type] = true;
    });

    this.articles = this.nodes
        .filter(node => node.type === 'Article')
        .sort((a, b) => a.label.localeCompare(b.label));

    this.articles.forEach(article => {
      this.selectedArticles[article.id] = true;
    });

    this.filteredNodes = [...this.nodes];
    this.filteredLinks = [...this.links];

    this.adjustNodePositions();
  }

  private adjustNodePositions() {
    this.nodes.forEach(node => {
      if (node.type !== 'Keyword' && node.type !== 'Article') {
        const jitter = 50;
        node.x += (Math.random() - 0.5) * jitter;
        node.y += (Math.random() - 0.5) * jitter;
      }
    });

    for (let i = 0; i < 10; i++) {
      this.nodes.forEach((node1, i) => {
        this.nodes.slice(i + 1).forEach(node2 => {
          const dx = node2.x - node1.x;
          const dy = node2.y - node1.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const minDistance = this.nodeRadius * 3;

          if (distance < minDistance) {
            const force = (minDistance - distance) / distance;
            const moveX = dx * force * 0.5;
            const moveY = dy * force * 0.5;

            node2.x += moveX;
            node2.y += moveY;
            node1.x -= moveX;
            node1.y -= moveY;

            this.constrainNodePosition(node1);
            this.constrainNodePosition(node2);
          }
        });
      });
    }
  }

  private constrainNodePosition(node: RDFNode) {
    const padding = this.nodeRadius * 2;
    node.x = Math.max(padding, Math.min(this.width - padding, node.x));
    node.y = Math.max(padding, Math.min(this.height - padding, node.y));
  }

  private determineNodeType(triple: RDFTriple): string {
    if (triple.p.value.includes('@type')) {
      const type = triple.o.value;
      if (type.includes('Person')) return 'Person';
      if (type.includes('Organization')) return 'Organization';
      if (type.includes('NewsArticle')) return 'Article';
      if (type.includes('ImageObject')) return 'Image';
    }

    if (triple.p.value.includes('author')) return 'Author';
    if (triple.p.value.includes('publisher')) return 'Publisher';
    if (triple.p.value.includes('keywords')) return 'Keyword';
    if (triple.p.value.includes('image')) return 'Image';
    if (triple.s.value.includes('article')) return 'Article';

    return 'Resource';
  }

  private getDisplayLabel(uri: string): string {
    if (uri.includes('article')) {
      const articleNode = this.nodes.find(n => n.id === uri);
      if (articleNode?.value) {
        return articleNode.value;
      }
    }

    const cleanUri = uri.split('^^')[0].replace(/^"|"$/g, '');

    if (cleanUri.includes('XMLSchema#')) {
      return cleanUri.split('"')[1] || cleanUri;
    }

    const parts = cleanUri.split(/[/#]/);
    const localName = parts[parts.length - 1];
    return decodeURIComponent(localName).replace(/_/g, ' ');
  }

  public getNodeColor(type: string): string {
    const colors: { [key: string]: string } = {
      'Article': '#FF4B4B',
      'Publisher': '#4CAF50',
      'Author': '#2196F3',
      'Keyword': '#9C27B0',
      'Language': '#FF9800',
      'Nationality': '#795548',
      'JobTitle': '#009688',
      'Section': '#607D8B',
      'Resource': '#757575',
      'Unknown': '#BDBDBD'
    };
    return colors[type] || colors['Unknown'];
  }

  private getLocalName(uri: string): string {
    const cleanUri = uri.split('^^')[0].replace(/^"|"$/g, '');

    if (cleanUri.includes('XMLSchema#')) {
      return cleanUri.split('"')[1] || cleanUri;
    }

    const parts = cleanUri.split(/[/#]/);
    return decodeURIComponent(parts[parts.length - 1]);
  }

  private isURI(value: string): boolean {
    return value.startsWith('http://') || value.startsWith('https://');
  }

  private initializeGraph() {
    console.log('Initializing graph');
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.setAttribute('width', '100%');
    this.svg.setAttribute('height', '100%');
    this.svg.setAttribute('viewBox', `0 0 ${this.width} ${this.height}`);
    this.svg.style.backgroundColor = '#f8f9fa';

    this.mainGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    this.svg.appendChild(this.mainGroup);

    this.setupEventListeners();

    this.svgContainer.nativeElement.innerHTML = '';
    this.svgContainer.nativeElement.appendChild(this.svg);
    console.log('Graph initialized');
  }


  private setupEventListeners() {
    if (!this.svg) return;

    document.addEventListener('mousemove', this.boundMouseMove);
    document.addEventListener('mouseup', this.boundMouseUp);
    this.svg.addEventListener('wheel', this.boundWheel);
    this.svg.addEventListener('contextmenu', this.boundContextMenu);

    this.svg.addEventListener('mousedown', (e: MouseEvent) => {
      if ((e.button === 1 || e.button === 2) && !this.isDragging) {
        this.isPanning = true;
        this.startPanX = e.clientX;
        this.startPanY = e.clientY;
        e.preventDefault();
      }
    });
  }

  private createGraphElements() {
    const mainGroup = this.mainGroup;
    if (!mainGroup) return;

    this.filteredLinks.forEach(link => {
      const source = this.filteredNodes.find(n => n.id === link.source);
      const target = this.filteredNodes.find(n => n.id === link.target);

      if (source && target) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('data-link-id', `${link.source}-${link.target}`);
        line.setAttribute('stroke', '#999');
        line.setAttribute('stroke-width', '2');

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('data-label-id', `${link.source}-${link.target}`);
        label.textContent = link.predicate;
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('class', 'text-xs fill-current');

        mainGroup.appendChild(line);
        mainGroup.appendChild(label);
      }
    });

    this.filteredNodes.forEach(node => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('data-node-id', node.id);
      g.setAttribute('cursor', 'grab');

      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', this.nodeRadius.toString());
      circle.setAttribute('fill', this.getNodeColor(node.type));
      circle.setAttribute('stroke', '#ffffff');
      circle.setAttribute('stroke-width', '2');

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.textContent = node.label;
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('class', 'text-sm');
      text.setAttribute('y', '40');

      g.appendChild(circle);
      g.appendChild(text);

      g.addEventListener('mousedown', (e: MouseEvent) => {
        if (e.button === 0) {
          this.selectedNode = node;
          this.isDragging = true;
          this.dragStartX = e.clientX;
          this.dragStartY = e.clientY;
          g.setAttribute('cursor', 'grabbing');
          e.stopPropagation();
          e.preventDefault();
        }
      });

      g.addEventListener('mouseenter', () => {
        if (!this.isDragging) {
          this.highlightNode(node.id);
          circle.setAttribute('r', (this.nodeRadius * 1.1).toString());
          circle.setAttribute('stroke-width', '3');
        }
      });

      g.addEventListener('mouseleave', () => {
        if (!this.isDragging && !this.searchResults.length) {
          this.resetHighlighting();
          circle.setAttribute('r', this.nodeRadius.toString());
          circle.setAttribute('stroke-width', '2');
        }
      });

      mainGroup.appendChild(g);
    });
  }

  private updateGraph() {
    const mainGroup = this.mainGroup;
    if (!mainGroup) return;

    this.filteredNodes.forEach(node => {
      if (isNaN(node.x) || isNaN(node.y)) {
        node.x = this.width / 2;
        node.y = this.height / 2;
      }

      const g = mainGroup.querySelector(`[data-node-id="${node.id}"]`);
      if (!g) return;

      const circle = g.querySelector('circle');
      const text = g.querySelector('text');

      if (circle && text) {
        circle.setAttribute('cx', `${node.x || this.width / 2}`);
        circle.setAttribute('cy', `${node.y || this.height / 2}`);
        text.setAttribute('x', `${node.x || this.width / 2}`);
        text.setAttribute('y', `${(node.y || this.height / 2) + 30}`);
      }
    });

    this.filteredLinks.forEach(link => {
      const source = this.filteredNodes.find(n => n.id === link.source);
      const target = this.filteredNodes.find(n => n.id === link.target);

      if (!source || !target) return;

      const line = mainGroup.querySelector(
          `[data-link-id="${link.source}-${link.target}"]`
      ) as SVGLineElement | null;

      const label = mainGroup.querySelector(
          `[data-label-id="${link.source}-${link.target}"]`
      ) as SVGTextElement | null;

      if (line) {
        line.setAttribute('x1', `${source.x || this.width / 2}`);
        line.setAttribute('y1', `${source.y || this.height / 2}`);
        line.setAttribute('x2', `${target.x || this.width / 2}`);
        line.setAttribute('y2', `${target.y || this.height / 2}`);
      }

      if (label) {
        label.setAttribute('x', `${((source.x || 0) + (target.x || 0)) / 2}`);
        label.setAttribute('y', `${((source.y || 0) + (target.y || 0)) / 2 - 10}`);
      }
    });
  }

  private handleMouseMove(e: MouseEvent) {
    if (!this.svg) return;

    if (this.isDragging && this.selectedNode) {
      const rect = this.svg.getBoundingClientRect();
      const scale = this.width / rect.width / this.currentZoom;

      const dx = (e.clientX - this.dragStartX) * scale;
      const dy = (e.clientY - this.dragStartY) * scale;

      this.selectedNode.x += dx;
      this.selectedNode.y += dy;

      this.selectedNode.x = Math.max(
          this.nodeRadius,
          Math.min(this.width - this.nodeRadius, this.selectedNode.x)
      );
      this.selectedNode.y = Math.max(
          this.nodeRadius,
          Math.min(this.height - this.nodeRadius, this.selectedNode.y)
      );

      this.dragStartX = e.clientX;
      this.dragStartY = e.clientY;

      this.updateGraph();
    } else if (this.isPanning) {
      const dx = (e.clientX - this.startPanX) / this.currentZoom;
      const dy = (e.clientY - this.startPanY) / this.currentZoom;

      this.viewboxX = this.svg.viewBox.baseVal.x;
      this.viewboxY = this.svg.viewBox.baseVal.y;

      this.svg.setAttribute(
          'viewBox',
          `${this.viewboxX - dx} ${this.viewboxY - dy} ${this.width / this.currentZoom} ${this.height / this.currentZoom}`
      );

      this.startPanX = e.clientX;
      this.startPanY = e.clientY;
    }
  }

  private handleMouseUp() {
    if (this.isDragging && this.selectedNode && this.mainGroup) {
      const g = this.mainGroup.querySelector(
          `[data-node-id="${this.selectedNode.id}"]`
      );
      if (g) g.setAttribute('cursor', 'grab');
    }

    this.selectedNode = null;
    this.isDragging = false;
    this.isPanning = false;
  }

  private handleWheel(e: WheelEvent) {
    e.preventDefault();
    if (!this.svg) return;

    const rect = this.svg.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    this.handleZoom(-e.deltaY, mouseX, mouseY);
  }

  private handleZoom(delta: number, mouseX: number, mouseY: number) {
    if (!this.svg) return;

    const zoomFactor = delta > 0 ? 1.1 : 0.9;
    const newZoom = Math.max(0.1, Math.min(4, this.currentZoom * zoomFactor));

    if (newZoom !== this.currentZoom) {
      const viewBox = this.svg.viewBox.baseVal;
      const dx = (mouseX - viewBox.x) * (1 - 1 / zoomFactor);
      const dy = (mouseY - viewBox.y) * (1 - 1 / zoomFactor);

      viewBox.x += dx;
      viewBox.y += dy;
      viewBox.width = this.width / newZoom;
      viewBox.height = this.height / newZoom;

      this.currentZoom = newZoom;
    }
  }

  zoomIn() {
    this.handleZoom(100, this.width/2, this.height/2);
  }


  zoomOut() {
    this.handleZoom(-100, this.width/2, this.height/2);
  }

  resetView() {
    if (this.svg) {
      this.svg.setAttribute('viewBox', `0 0 ${this.width} ${this.height}`);
      this.currentZoom = 1;
    }
  }

  search() {
    const term = this.searchTerm.toLowerCase();
    if (!term) {
      this.resetHighlighting();
      this.searchResults = [];
      return;
    }

    this.searchResults = this.nodes.filter(node =>
        node.label.toLowerCase().includes(term) ||
        node.type.toLowerCase().includes(term)
    );

    this.resetHighlighting();
    this.searchResults.forEach(node => {
      this.highlightNode(node.id, true);
    });
  }

  public highlightNode(nodeId: string, isSearch = false) {
    if (!this.mainGroup) return;

    this.resetHighlighting();
    this.highlightedNodeId = nodeId;

    const connectedLinks = this.links.filter(
        link => link.source === nodeId || link.target === nodeId
    );
    const connectedNodeIds = new Set(
        connectedLinks.flatMap(link => [link.source, link.target])
    );

    this.nodes.forEach(node => {
      const nodeElement = this.mainGroup!.querySelector(
          `[data-node-id="${node.id}"]`
      );
      if (nodeElement) {
        nodeElement.setAttribute('opacity', this.fadedOpacity);
      }
    });

    this.links.forEach(link => {
      const linkElement = this.mainGroup!.querySelector(
          `[data-link-id="${link.source}-${link.target}"]`
      );
      const labelElement = this.mainGroup!.querySelector(
          `[data-label-id="${link.source}-${link.target}"]`
      );
      if (linkElement) linkElement.setAttribute('opacity', this.fadedOpacity);
      if (labelElement) labelElement.setAttribute('opacity', this.fadedOpacity);
    });

    connectedNodeIds.forEach(id => {
      const nodeElement = this.mainGroup!.querySelector(
          `[data-node-id="${id}"]`
      );
      if (nodeElement) {
        nodeElement.setAttribute('opacity', this.defaultOpacity);
        if (id === nodeId) {
          const circle = nodeElement.querySelector('circle');
          if (circle) {
            circle.setAttribute('stroke', '#000');
            circle.setAttribute('stroke-width', '3');
          }
        }
      }
    });

    connectedLinks.forEach(link => {
      const linkElement = this.mainGroup!.querySelector(
          `[data-link-id="${link.source}-${link.target}"]`
      );
      const labelElement = this.mainGroup!.querySelector(
          `[data-label-id="${link.source}-${link.target}"]`
      );
      if (linkElement) {
        linkElement.setAttribute('opacity', this.defaultOpacity);
        linkElement.setAttribute('stroke-width', '3');
      }
      if (labelElement) labelElement.setAttribute('opacity', this.defaultOpacity);
    });
  }

  private resetHighlighting() {
    if (!this.mainGroup) return;

    this.highlightedNodeId = null;

    this.nodes.forEach(node => {
      const nodeElement = this.mainGroup!.querySelector(
          `[data-node-id="${node.id}"]`
      );
      if (nodeElement) {
        nodeElement.setAttribute('opacity', this.defaultOpacity);
        const circle = nodeElement.querySelector('circle');
        if (circle) {
          circle.setAttribute('stroke', 'none');
          circle.setAttribute('stroke-width', '0');
        }
      }
    });

    this.links.forEach((link: RDFLink) => {
      const linkElement = this.mainGroup!.querySelector(
          `[data-link-id="${link.source}-${link.target}"]`
      );
      const labelElement = this.mainGroup!.querySelector(
          `[data-label-id="${link.source}-${link.target}"]`
      );
      if (linkElement) {
        linkElement.setAttribute('opacity', this.defaultOpacity);
        linkElement.setAttribute('stroke-width', '2');
      }
      if (labelElement) labelElement.setAttribute('opacity', this.defaultOpacity);
    });
  }
}
