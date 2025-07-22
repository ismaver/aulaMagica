
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:5000'
};
export const apiEndpoints = {
  generateImage: `${environment.apiBaseUrl}/generate`,
  getQuestions: `${environment.apiBaseUrl}/questions`,
  playTTS: `${environment.apiBaseUrl}/tts`,
  sendAudio: `${environment.apiBaseUrl}/stt`,
  evaluate: `${environment.apiBaseUrl}/evaluate`
};