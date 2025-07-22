import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AulaMagicaComponent } from './aula-magica.component';

describe('AulaMagicaComponent', () => {
  let component: AulaMagicaComponent;
  let fixture: ComponentFixture<AulaMagicaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AulaMagicaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AulaMagicaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
