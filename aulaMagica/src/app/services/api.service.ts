// src/app/services/api.service.ts
import { Injectable }   from '@angular/core';
import { HttpClient }   from '@angular/common/http';
import { Observable }   from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

interface ImgRes    { image_url: string; }
interface QsRes     { questions: string[]; }
interface Feedback  { feedback: string; }
interface SttRes    { text: string; }

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = '/api';

  constructor(private http: HttpClient) {}

  generateImage(prompt: string): Observable<ImgRes> {
    return this.http.post<ImgRes>(`${this.base}/generate`, { prompt });
  }

  getQuestions(prompt: string): Observable<QsRes> {
    return this.http.post<QsRes>(`${this.base}/questions`, { prompt });
  }

  playTTS(text: string): Observable<Blob> {
    return this.http.post(`${this.base}/tts`, { text }, { responseType: 'blob' });
  }

  sendAudio(blob: Blob): Observable<SttRes> {
    const form = new FormData();
    form.append('audio', blob, 'response.webm');
    return this.http.post<SttRes>(`${this.base}/stt`, form);
  }

  evaluate(question: string, answer: string): Observable<Feedback> {
    return this.http.post<Feedback>(`${this.base}/evaluate`, { question, answer });
  }
}
