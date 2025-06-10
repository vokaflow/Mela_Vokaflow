/* ================================================
   VokaFlow WebApp - JavaScript Común
   ================================================ */

// Configuración global
const VokaFlow = {
    apiBaseUrl: '/api',
    backendUrl: 'http://localhost:8000',
    version: '1.0.0',
    debug: true
};

// Utilidades de logging
const Logger = {
    info: (message, ...args) => {
        if (VokaFlow.debug) {
            console.log(`[VokaFlow] ${message}`, ...args);
        }
    },

    error: (message, ...args) => {
        console.error(`[VokaFlow Error] ${message}`, ...args);
    },

    warn: (message, ...args) => {
        console.warn(`[VokaFlow Warning] ${message}`, ...args);
    }
};

// Sistema de notificaciones
const Notifications = {
    container: null,

    init() {
        this.container = document.getElementById('notification-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 5000) {
        this.init();

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        // Icono según el tipo
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        notification.innerHTML = `
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        this.container.appendChild(notification);

        // Auto-remover después del tiempo especificado
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }

        return notification;
    },

    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    },

    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    },

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    },

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }
};

// Utilidades de loading
const Loading = {
    overlay: null,

    init() {
        this.overlay = document.getElementById('loading-overlay');
    },

    show(text = 'Procesando...') {
        this.init();
        if (this.overlay) {
            const loadingText = document.getElementById('loading-text');
            if (loadingText) {
                loadingText.textContent = text;
            }
            this.overlay.style.display = 'flex';
        }
    },

    hide() {
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }
    }
};

// Cliente HTTP
const ApiClient = {
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        const requestOptions = { ...defaultOptions, ...options };

        try {
            Logger.info(`API Request: ${requestOptions.method || 'GET'} ${url}`);

            const response = await fetch(url, requestOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            Logger.info(`API Response: ${response.status}`, data);
            return data;
        } catch (error) {
            Logger.error(`API Error: ${error.message}`);
            throw error;
        }
    },

    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(fullUrl);
    },

    async post(url, data = {}, options = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    },

    async postFormData(url, formData, options = {}) {
        // No establecer Content-Type para FormData, el navegador lo hará automáticamente
        const headers = { ...options.headers };
        delete headers['Content-Type'];

        return this.request(url, {
            method: 'POST',
            body: formData,
            headers,
            ...options
        });
    }
};

// Gestión de estado del sistema
const SystemStatus = {
    status: {
        backend: 'unknown',
        ai_configured: false,
        features: {}
    },

    async check() {
        try {
            const response = await ApiClient.get(`${VokaFlow.apiBaseUrl}/status`);
            this.status = response;
            this.updateUI();
            return response;
        } catch (error) {
            Logger.error('Error checking system status:', error);
            this.status.backend = 'offline';
            this.updateUI();
            return null;
        }
    },

    updateUI() {
        // Actualizar indicador de estado en el navbar
        const statusBtn = document.getElementById('status-btn');
        const backendStatus = document.getElementById('backend-status');

        if (statusBtn) {
            const circle = statusBtn.querySelector('.fa-circle');
            if (circle) {
                circle.className = 'fas fa-circle';
                if (this.status.backend === 'online') {
                    circle.style.color = 'var(--success-color)';
                    statusBtn.title = 'Sistema online';
                } else if (this.status.backend === 'offline') {
                    circle.style.color = 'var(--error-color)';
                    statusBtn.title = 'Sistema offline';
                } else {
                    circle.style.color = 'var(--warning-color)';
                    statusBtn.title = 'Estado desconocido';
                }
            }
        }

        if (backendStatus) {
            backendStatus.textContent = this.status.backend === 'online' ? 'Online' : 'Offline';
            backendStatus.className = this.status.backend === 'online' ? 'text-success' : 'text-error';
        }
    }
};

// Gestión de temas
const ThemeManager = {
    currentTheme: 'light',

    init() {
        // Cargar tema guardado
        const savedTheme = localStorage.getItem('vokaflow-theme');
        if (savedTheme) {
            this.setTheme(savedTheme);
        }

        // Configurar botón de toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    },

    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('vokaflow-theme', theme);

        // Actualizar icono del botón
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }

        Logger.info(`Theme changed to: ${theme}`);
    },

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
};

// Utilidades generales
const Utils = {
    // Formatear tiempo en formato mm:ss
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    // Copiar texto al portapapeles
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            Notifications.success('Texto copiado al portapapeles');
            return true;
        } catch (error) {
            Logger.error('Error copying to clipboard:', error);
            Notifications.error('Error al copiar al portapapeles');
            return false;
        }
    },

    // Validar email
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function () {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Generar ID único
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
};

// Audio utilities
const AudioUtils = {
    // Reproducir audio desde URL
    async playAudioFromUrl(url) {
        try {
            const audio = document.getElementById('audio-player') || document.createElement('audio');
            audio.id = 'audio-player';
            audio.preload = 'none';

            if (!document.getElementById('audio-player')) {
                document.body.appendChild(audio);
            }

            audio.src = url;
            await audio.play();

            Logger.info('Audio playback started');
            return audio;
        } catch (error) {
            Logger.error('Error playing audio:', error);
            Notifications.error('Error al reproducir audio');
            throw error;
        }
    },

    // Reproducir audio desde base64
    async playAudioFromBase64(base64Data, format = 'wav') {
        try {
            const audioBlob = this.base64ToBlob(base64Data, `audio/${format}`);
            const audioUrl = URL.createObjectURL(audioBlob);

            const audio = await this.playAudioFromUrl(audioUrl);

            // Limpiar URL después de reproducir
            audio.addEventListener('ended', () => {
                URL.revokeObjectURL(audioUrl);
            });

            return audio;
        } catch (error) {
            Logger.error('Error playing base64 audio:', error);
            throw error;
        }
    },

    // Convertir base64 a Blob
    base64ToBlob(base64, mimeType) {
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);

        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: mimeType });
    }
};

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    Logger.info('VokaFlow WebApp initialized');

    // Inicializar componentes
    ThemeManager.init();
    SystemStatus.check();

    // Configurar navegación con data attributes
    document.addEventListener('click', function (e) {
        const target = e.target.closest('[data-action="navigate"]');
        if (target) {
            const url = target.dataset.url;
            if (url) {
                window.location.href = url;
            }
        }
    });

    // Verificar estado del sistema cada 30 segundos
    setInterval(() => {
        SystemStatus.check();
    }, 30000);
});

// Funciones globales para usar en HTML
window.testMicrophone = async function () {
    try {
        Loading.show('Probando micrófono...');

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Parar el stream inmediatamente
        stream.getTracks().forEach(track => track.stop());

        Loading.hide();
        Notifications.success('Micrófono funcionando correctamente');
    } catch (error) {
        Loading.hide();
        Logger.error('Microphone test failed:', error);
        Notifications.error('Error al acceder al micrófono. Verifica los permisos.');
    }
};

window.checkSystemStatus = async function () {
    Loading.show('Verificando sistema...');

    const status = await SystemStatus.check();

    Loading.hide();

    if (status) {
        Notifications.success('Sistema funcionando correctamente');
    } else {
        Notifications.error('Error al verificar el estado del sistema');
    }
};

// Exportar para uso en otros scripts
window.VokaFlow = VokaFlow;
window.Logger = Logger;
window.Notifications = Notifications;
window.Loading = Loading;
window.ApiClient = ApiClient;
window.SystemStatus = SystemStatus;
window.ThemeManager = ThemeManager;
window.Utils = Utils;
window.AudioUtils = AudioUtils;
