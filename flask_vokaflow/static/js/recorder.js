/* ================================================
   VokaFlow WebApp - Grabador de Audio
   ================================================ */

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.startTime = null;
        this.onDataCallback = null;
        this.onStopCallback = null;
        this.onErrorCallback = null;
    }

    // Verificar soporte del navegador
    static isSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);
    }

    // Inicializar grabador
    async init() {
        if (!AudioRecorder.isSupported()) {
            throw new Error('Tu navegador no soporta grabación de audio');
        }

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 16000
                }
            });

            // Verificar tipos MIME soportados
            const mimeTypes = [
                'audio/webm;codecs=opus',
                'audio/webm',
                'audio/ogg;codecs=opus',
                'audio/mp4',
                'audio/wav'
            ];

            let selectedMimeType = '';
            for (const mimeType of mimeTypes) {
                if (MediaRecorder.isTypeSupported(mimeType)) {
                    selectedMimeType = mimeType;
                    break;
                }
            }

            if (!selectedMimeType) {
                throw new Error('No se encontró un formato de audio compatible');
            }

            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: selectedMimeType
            });

            this.setupEventListeners();
            Logger.info(`Audio recorder initialized with ${selectedMimeType}`);

        } catch (error) {
            Logger.error('Error initializing audio recorder:', error);
            throw error;
        }
    }

    // Configurar event listeners
    setupEventListeners() {
        this.mediaRecorder.addEventListener('dataavailable', (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
            }
        });

        this.mediaRecorder.addEventListener('stop', async () => {
            const audioBlob = new Blob(this.audioChunks, {
                type: this.mediaRecorder.mimeType
            });

            this.audioChunks = [];

            if (this.onStopCallback) {
                await this.onStopCallback(audioBlob);
            }
        });

        this.mediaRecorder.addEventListener('error', (event) => {
            Logger.error('MediaRecorder error:', event.error);
            if (this.onErrorCallback) {
                this.onErrorCallback(event.error);
            }
        });

        this.mediaRecorder.addEventListener('start', () => {
            this.startTime = Date.now();
            this.isRecording = true;
            Logger.info('Recording started');
        });
    }

    // Empezar grabación
    async startRecording() {
        if (!this.mediaRecorder) {
            await this.init();
        }

        if (this.isRecording) {
            Logger.warn('Recording already in progress');
            return;
        }

        try {
            this.audioChunks = [];
            this.mediaRecorder.start(1000); // Capturar datos cada segundo
        } catch (error) {
            Logger.error('Error starting recording:', error);
            throw error;
        }
    }

    // Parar grabación
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            Logger.warn('No recording in progress');
            return;
        }

        try {
            this.mediaRecorder.stop();
            this.isRecording = false;
        } catch (error) {
            Logger.error('Error stopping recording:', error);
            throw error;
        }
    }

    // Obtener duración de grabación actual
    getRecordingDuration() {
        if (!this.startTime) return 0;
        return (Date.now() - this.startTime) / 1000;
    }

    // Limpiar recursos
    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.startTime = null;
    }

    // Configurar callbacks
    onData(callback) {
        this.onDataCallback = callback;
    }

    onStop(callback) {
        this.onStopCallback = callback;
    }

    onError(callback) {
        this.onErrorCallback = callback;
    }
}

// Utilidad para convertir Blob a base64
function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64 = reader.result.split(',')[1]; // Remover el prefijo data:audio/...;base64,
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

// Utilidad para convertir Blob a ArrayBuffer
function blobToArrayBuffer(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsArrayBuffer(blob);
    });
}

// Clase para manejar botones de grabación
class RecordButton {
    constructor(buttonElement, options = {}) {
        this.button = buttonElement;
        this.recorder = new AudioRecorder();
        this.isRecording = false;
        this.recordingInterval = null;
        this.onRecordingComplete = options.onComplete || null;
        this.onRecordingStart = options.onStart || null;
        this.onRecordingStop = options.onStop || null;
        this.onError = options.onError || null;
        this.maxDuration = options.maxDuration || 300; // 5 minutos por defecto

        this.init();
    }

    init() {
        this.setupRecorder();
        this.setupButton();
    }

    setupRecorder() {
        this.recorder.onStop(async (audioBlob) => {
            this.stopRecordingUI();

            if (this.onRecordingComplete) {
                try {
                    await this.onRecordingComplete(audioBlob);
                } catch (error) {
                    Logger.error('Error in recording complete callback:', error);
                    if (this.onError) {
                        this.onError(error);
                    }
                }
            }
        });

        this.recorder.onError((error) => {
            this.stopRecordingUI();
            Logger.error('Recording error:', error);

            if (this.onError) {
                this.onError(error);
            } else {
                Notifications.error('Error en la grabación: ' + error.message);
            }
        });
    }

    setupButton() {
        // Soporte para click y mantener presionado
        this.button.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        this.button.addEventListener('mouseup', (e) => {
            e.preventDefault();
            if (this.isRecording) {
                this.stopRecording();
            }
        });

        this.button.addEventListener('mouseleave', (e) => {
            if (this.isRecording) {
                this.stopRecording();
            }
        });

        // Soporte para touch devices
        this.button.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        this.button.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (this.isRecording) {
                this.stopRecording();
            }
        });

        // Click simple como alternativa
        this.button.addEventListener('click', (e) => {
            e.preventDefault();
            if (!this.isRecording) {
                this.toggleRecording();
            }
        });
    }

    async startRecording() {
        if (this.isRecording) return;

        try {
            await this.recorder.startRecording();
            this.startRecordingUI();

            if (this.onRecordingStart) {
                this.onRecordingStart();
            }

            // Auto-stop después del tiempo máximo
            setTimeout(() => {
                if (this.isRecording) {
                    this.stopRecording();
                    Notifications.warning(`Grabación automáticamente detenida después de ${this.maxDuration} segundos`);
                }
            }, this.maxDuration * 1000);

        } catch (error) {
            Logger.error('Error starting recording:', error);
            if (this.onError) {
                this.onError(error);
            } else {
                Notifications.error('Error al iniciar grabación: ' + error.message);
            }
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        try {
            this.recorder.stopRecording();

            if (this.onRecordingStop) {
                this.onRecordingStop();
            }
        } catch (error) {
            Logger.error('Error stopping recording:', error);
            this.stopRecordingUI();
        }
    }

    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecordingUI() {
        this.isRecording = true;
        this.button.classList.add('recording');

        const icon = this.button.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-stop';
        }

        // Actualizar indicador visual si existe
        const indicator = this.button.querySelector('.voice-indicator');
        if (indicator) {
            indicator.classList.add('active');
        }

        // Actualizar título
        this.button.title = 'Suelta para parar la grabación';
    }

    stopRecordingUI() {
        this.isRecording = false;
        this.button.classList.remove('recording');

        const icon = this.button.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-microphone';
        }

        // Actualizar indicador visual si existe
        const indicator = this.button.querySelector('.voice-indicator');
        if (indicator) {
            indicator.classList.remove('active');
        }

        // Restaurar título
        this.button.title = 'Mantén presionado para grabar';
    }

    // Limpiar recursos
    destroy() {
        this.recorder.cleanup();

        if (this.recordingInterval) {
            clearInterval(this.recordingInterval);
        }
    }
}

// Exportar para uso global
window.AudioRecorder = AudioRecorder;
window.RecordButton = RecordButton;
window.blobToBase64 = blobToBase64;
window.blobToArrayBuffer = blobToArrayBuffer;
