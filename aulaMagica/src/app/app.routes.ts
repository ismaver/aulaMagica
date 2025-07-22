import { Routes } from '@angular/router';
import { HomeComponent }       from './home/home.component';
import { RulesComponent }      from './rules/rules.component';
import { AulaMagicaComponent } from './aula-magica/aula-magica.component';
import { ContactComponent }    from './contact/contact.component';

export const routes: Routes = [
  { path: '',            component: HomeComponent },
  { path: 'reglas',      component: RulesComponent },
  { path: 'aula-magica', component: AulaMagicaComponent },
  { path: 'contacto',    component: ContactComponent },
  { path: '**',          redirectTo: '' }
];