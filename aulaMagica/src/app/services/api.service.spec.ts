import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiService } from './api.service';
import { environment } from '../../environments/environment';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ApiService]
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('should request image URL', () => {
    const mock = { image_url: 'url.png' };
    service.generateImage('hey').subscribe(res => expect(res.image_url).toBe('url.png'));
    const req = httpMock.expectOne(`${environment.apiBaseUrl}/generate`);
    expect(req.request.method).toBe('POST');
    req.flush(mock);
  });
});
