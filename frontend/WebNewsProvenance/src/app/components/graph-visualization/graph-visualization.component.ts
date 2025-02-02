import { Component, ElementRef, OnInit, ViewChild, OnDestroy } from '@angular/core';

interface Node {
  id: string;
  label: string;
  type: string;
  x: number;
  y: number;
}

interface Link {
  source: string;
  target: string;
  label: string;
}

interface NodeData {
  id: string;
  label: string;
  type: string;
}

@Component({
  selector: 'app-graph-visualization',
  templateUrl: './graph-visualization.component.html',
  styleUrls: ['./graph-visualization.component.scss']
})
export class GraphVisualizationComponent implements OnInit {

  @ViewChild('svgContainer', { static: true }) svgContainer!: ElementRef<HTMLDivElement>;
  @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

  searchTerm: string = '';
  searchResults: Node[] = [];
  private highlightedNodeId: string | null = null;
  private defaultOpacity = '1';
  private fadedOpacity = '0.2';

  private width = 800;
  private height = 600;
  private nodeRadius = 20;
  private svg: SVGSVGElement | null = null;
  private mainGroup: SVGGElement | null = null;

  private currentZoom = 1;
  private viewboxX = 0;
  private viewboxY = 0;
  private isPanning = false;
  private startPanX = 0;
  private startPanY = 0;

  private selectedNode: Node | null = null;
  private isDragging = false;
  private dragStartX = 0;
  private dragStartY = 0;

  // Bound event handlers
  private boundMouseMove: (e: MouseEvent) => void;
  private boundMouseUp: (e: MouseEvent) => void;
  private boundWheel: (e: WheelEvent) => void;
  private boundContextMenu: (e: Event) => void;

  nodeTypes = ['Person', 'University', 'Publication', 'Topic'];

  private sampleData: { nodes: NodeData[], links: Link[] } = {
    nodes: [
      { id: 'Person1', label: 'John Doe', type: 'Person' },
      { id: 'University1', label: 'MIT', type: 'University' },
      { id: 'Paper1', label: 'Research Paper A', type: 'Publication' },
      { id: 'Person2', label: 'Jane Smith', type: 'Person' },
      { id: 'Topic1', label: 'Machine Learning', type: 'Topic' }
    ],
    links: [
      { source: 'Person1', target: 'University1', label: 'studiedAt' },
      { source: 'Person1', target: 'Paper1', label: 'authored' },
      { source: 'Person2', target: 'Paper1', label: 'authored' },
      { source: 'Paper1', target: 'Topic1', label: 'about' }
    ]
  };

  private nodes: Node[] = [];

  constructor() {
    // Bind event handlers to maintain correct 'this' context
    this.boundMouseMove = this.handleMouseMove.bind(this);
    this.boundMouseUp = this.handleMouseUp.bind(this);
    this.boundWheel = this.handleWheel.bind(this);
    this.boundContextMenu = (e: Event) => e.preventDefault();
  }

  ngOnInit() {
    this.initializeGraph();
  }

  ngOnDestroy() {
    // Remove event listeners on component destroy
    document.removeEventListener('mousemove', this.boundMouseMove);
    document.removeEventListener('mouseup', this.boundMouseUp);
    this.svg?.removeEventListener('wheel', this.boundWheel);
    this.svg?.removeEventListener('contextmenu', this.boundContextMenu);
  }

  private initializeGraph() {
    // Initialize nodes with positions
    this.nodes = this.sampleData.nodes.map(node => ({
      ...node,
      x: Math.random() * (this.width - 2 * this.nodeRadius) + this.nodeRadius,
      y: Math.random() * (this.height - 2 * this.nodeRadius) + this.nodeRadius,
    }));

    // Set up SVG
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.setAttribute('width', '100%');
    this.svg.setAttribute('height', '100%');
    this.svg.setAttribute('viewBox', `0 0 ${this.width} ${this.height}`);

    this.mainGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    this.svg.appendChild(this.mainGroup);

    // Add event listeners
    this.setupEventListeners();

    // Create initial graph
    this.createGraphElements();
    this.updateGraph();

    // Add to DOM
    this.svgContainer.nativeElement.appendChild(this.svg);
  }

  private setupEventListeners() {
    if (!this.svg) return;

    // Add event listeners to document for better drag handling
    document.addEventListener('mousemove', this.boundMouseMove);
    document.addEventListener('mouseup', this.boundMouseUp);

    // Add SVG-specific listeners
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

  private handleWheel(e: WheelEvent) {
    e.preventDefault();
    if (!this.svg) return;

    const rect = this.svg.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    this.handleZoom(-e.deltaY, mouseX, mouseY);
  }

  private createGraphElements() {
    const mainGroup = this.mainGroup;
    if (!mainGroup) return;

    // Clear existing elements
    while (mainGroup.firstChild) {
      mainGroup.removeChild(mainGroup.firstChild);
    }

    // Create links first (so they appear behind nodes)
    this.sampleData.links.forEach(link => {
      const source = this.nodes.find(n => n.id === link.source);
      const target = this.nodes.find(n => n.id === link.target);

      if (source && target) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('data-link-id', `${link.source}-${link.target}`);
        line.setAttribute('stroke', '#999');
        line.setAttribute('stroke-width', '2');

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('data-label-id', `${link.source}-${link.target}`);
        label.textContent = link.label;
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('class', 'text-xs fill-current');

        mainGroup.appendChild(line);
        mainGroup.appendChild(label);
      }
    });

    // Create nodes
    this.nodes.forEach(node => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('data-node-id', node.id);
      g.setAttribute('cursor', 'grab');

      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', this.nodeRadius.toString());
      circle.setAttribute('fill', this.getNodeColor(node.type));

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.textContent = node.label;
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('class', 'text-sm fill-current');

      g.appendChild(circle);
      g.appendChild(text);

      g.addEventListener('mousedown', (e: MouseEvent) => {
        if (e.button === 0) { // Left click only
          this.selectedNode = node;
          this.isDragging = true;
          this.dragStartX = e.clientX;
          this.dragStartY = e.clientY;
          g.setAttribute('cursor', 'grabbing');
          e.stopPropagation();
          e.preventDefault();
        }
      });

      // Add hover and click effects
      g.addEventListener('mouseenter', () => {
        if (!this.isDragging) {
          this.highlightNode(node.id);
        }
      });

      g.addEventListener('mouseleave', () => {
        if (!this.isDragging && !this.searchResults.length) {
          this.resetHighlighting();
        }
      });

      mainGroup.appendChild(g);
    });
  }

  private updateGraph() {
    const mainGroup = this.mainGroup;
    if (!mainGroup) return;

    this.nodes.forEach(node => {
      const g = mainGroup.querySelector(`[data-node-id="${node.id}"]`);
      if (!g) return;

      const circle = g.querySelector('circle');
      const text = g.querySelector('text');

      if (circle && text) {
        circle.setAttribute('cx', node.x.toString());
        circle.setAttribute('cy', node.y.toString());
        text.setAttribute('x', node.x.toString());
        text.setAttribute('y', (node.y + 30).toString());
      }
    });

    this.sampleData.links.forEach(link => {
      const source = this.nodes.find(n => n.id === link.source);
      const target = this.nodes.find(n => n.id === link.target);

      if (!source || !target) return;

      const line = mainGroup.querySelector(
        `[data-link-id="${link.source}-${link.target}"]`
      ) as SVGLineElement | null;
      const label = mainGroup.querySelector(
        `[data-label-id="${link.source}-${link.target}"]`
      ) as SVGTextElement | null;

      if (line) {
        line.setAttribute('x1', source.x.toString());
        line.setAttribute('y1', source.y.toString());
        line.setAttribute('x2', target.x.toString());
        line.setAttribute('y2', target.y.toString());
      }

      if (label) {
        label.setAttribute('x', ((source.x + target.x) / 2).toString());
        label.setAttribute('y', ((source.y + target.y) / 2).toString());
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

      // Constrain node position
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
    const mainGroup = this.mainGroup;
    if (this.isDragging && this.selectedNode && mainGroup) {
      const g = mainGroup.querySelector(
        `[data-node-id="${this.selectedNode.id}"]`
      );
      if (g) g.setAttribute('cursor', 'grab');
    }

    this.selectedNode = null;
    this.isDragging = false;
    this.isPanning = false;
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

  getNodeColor(type: string): string {
    const colors: { [key: string]: string } = {
      'Person': '#4299e1',
      'University': '#48bb78',
      'Publication': '#ed8936',
      'Topic': '#9f7aea'
    };
    return colors[type] || '#a0aec0';
  }

  zoomIn() {
    this.handleZoom(-100, this.width/2, this.height/2);
  }


  zoomOut() {
    this.handleZoom(100, this.width/2, this.height/2);
  }

  resetView() {
    if (this.svg) {
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

    // Highlight search results
    this.resetHighlighting();
    this.searchResults.forEach(node => {
      this.highlightNode(node.id, true);
    });
  }

  public highlightNode(nodeId: string, isSearch = false) {
    if (!this.mainGroup) return;

    this.resetHighlighting();
    this.highlightedNodeId = nodeId;

    // Find connected nodes and links
    const connectedLinks = this.sampleData.links.filter(
      link => link.source === nodeId || link.target === nodeId
    );
    const connectedNodeIds = new Set(
      connectedLinks.flatMap(link => [link.source, link.target])
    );

    // Fade all nodes and links
    this.nodes.forEach(node => {
      const nodeElement = this.mainGroup!.querySelector(
        `[data-node-id="${node.id}"]`
      );
      if (nodeElement) {
        nodeElement.setAttribute('opacity', this.fadedOpacity);
      }
    });

    this.sampleData.links.forEach(link => {
      const linkElement = this.mainGroup!.querySelector(
        `[data-link-id="${link.source}-${link.target}"]`
      );
      const labelElement = this.mainGroup!.querySelector(
        `[data-label-id="${link.source}-${link.target}"]`
      );
      if (linkElement) linkElement.setAttribute('opacity', this.fadedOpacity);
      if (labelElement) labelElement.setAttribute('opacity', this.fadedOpacity);
    });

    // Highlight connected elements
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

    // Reset all nodes
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

    // Reset all links
    this.sampleData.links.forEach(link => {
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
