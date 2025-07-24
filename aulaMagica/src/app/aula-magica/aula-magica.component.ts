import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule }    from '@angular/common';
import { FormsModule }     from '@angular/forms';
import { HttpClientModule }from '@angular/common/http';
import { ApiService }      from '../services/api.service';

@Component({
  selector: 'app-aula-magica',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './aula-magica.component.html',
  styleUrls: ['./aula-magica.component.css']
})
export class AulaMagicaComponent {
  prompt = '';
  loading = false;
  error = '';

  imageUrl = '';

  questions: string[] = [];
  currentIndex = 0;
  feedback = '';
  showNext = false;
  evaluationLoading = false;

  recording = false;
  private mediaRecorder!: MediaRecorder;
  private chunks: BlobPart[] = [];

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  onGenerate() {
    if (!this.prompt.trim()) return;
    this.resetState();
    this.loading = true;

    // 1) Generar imagen
    this.api.generateImage(this.prompt).subscribe({
      next: res => {console.log(res)
        this.imageUrl = "/ultima-imagen"},
      error: err => this.error = err.message || 'Error al generar imagen.',
      complete: () => {
        // 2) Generar preguntas
        this.api.getQuestions(this.prompt).subscribe({
          next: res => {
            console.log(this)
            this.questions = res.questions;
            this.currentIndex = 0;
            this.loadQuestion();
          },
          error: err => this.error = err.message || 'Error al generar preguntas.',
          complete: () => {
            this.loading = false;
            this.cdr.detectChanges();
          }
        });
      }
    });
  }

  private loadQuestion() {
    this.feedback = '';
    this.showNext = false;
    this.evaluationLoading = false;
    this.cdr.detectChanges();
  }

  onPlay() {
    const text = this.questions[this.currentIndex];
    this.api.playTTS(text).subscribe(blob => {
      const url = URL.createObjectURL(blob);
      new Audio(url).play();
    });
  }

  async onRecord() {
    if (!this.recording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.chunks = [];
      this.mediaRecorder.ondataavailable = e => this.chunks.push(e.data);
      this.mediaRecorder.onstop = () => {
        this.recording = false;
        this.processAudio();
      };
      this.mediaRecorder.start();
      this.recording = true;
    } else {
      this.mediaRecorder.stop();
    }
  }

  private processAudio() {
    this.evaluationLoading = true;
    this.cdr.detectChanges();

    const blob = new Blob(this.chunks, { type: 'audio/webm' });
    this.api.sendAudio(blob).subscribe({
      next: stt => {
        const answer = stt.text || '';
        this.api.evaluate(this.questions[this.currentIndex], answer)
          .subscribe({
            next: ev => {
              this.feedback = ev.feedback;
              this.showNext = true;
              this.evaluationLoading = false;
              this.cdr.detectChanges();
            },
            error: () => {
              this.error = 'Error al evaluar respuesta.';
              this.evaluationLoading = false;
              this.cdr.detectChanges();
            }
          });
      },
      error: () => {
        this.error = 'Error en STT.';
        this.evaluationLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  onNext() {
    this.currentIndex++;
    this.loadQuestion();
  }

  private resetState() {
    this.loading = this.showNext = this.recording = this.evaluationLoading = false;
    this.error = '';
    this.imageUrl = '';
    this.questions = [];
    this.currentIndex = 0;
    this.feedback = '';
  }
}
