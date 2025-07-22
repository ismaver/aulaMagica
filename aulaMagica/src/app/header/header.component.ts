import { Component }      from '@angular/core';
import { RouterModule }   from '@angular/router';
// (opcionalmente) CommonModule si vas a usar ngIf, ngFor, etc.
import { CommonModule }   from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {}