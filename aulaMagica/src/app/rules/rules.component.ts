import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-rules',
  imports: [],
  templateUrl: './rules.component.html',
  styleUrl: './rules.component.css',
  standalone: true
})
export class RulesComponent {
  constructor(private router: Router) { }

  goToAula(event: MouseEvent) {
    event.preventDefault();            // evita el reload de href
    this.router.navigate(['/aula-magica']);
  }
}
