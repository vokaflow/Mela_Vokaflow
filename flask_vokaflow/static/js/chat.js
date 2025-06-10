/* ================================================
   VokaFlow - Chat con IA - JavaScript
   ================================================ */

class VokaFlowChat {
    constructor() {
        this.chatHistory = [];
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentAudioUrl = null;
        this.settings = {
            aiProvider: 'deepseek-local',
            voiceEnabled: true,
            autoPlay: false,
            languageInput: 'es',
            voiceSpeed: 1.0
        };

        this.init();
    }

    init() {
        this.loadSettings();
        this.bindEvents();
        this.updateUI();
        this.checkStatus();

        // Auto-resize textarea
        this.setupTextareaResize();

        console.log('VokaFlow Chat inicializado');
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('vokaflow_chat_settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
    }

    saveSettings() {
        localStorage.setItem('vokaflow_chat_settings', JSON.stringify(this.settings));
    }

    bindEvents() {
        // Botones principales
        document.getElementById('send-button').addEventListener('click', () => this.sendMessage());
        document.getElementById('clear-chat').addEventListener('click', () => this.clearChat());
        document.getElementById('voice-toggle').addEventListener('click', () => this.toggleVoice());
        document.getElementById('settings-toggle').addEventListener('click', () => this.toggleSettings());
        document.getElementById('close-settings').addEventListener('click', () => this.toggleSettings());

        // Input de mensaje
        const messageInput = document.getElementById('message-input');
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        messageInput.addEventListener('input', () => this.updateCharCounter());

        // Botón de voz
        const voiceButton = document.getElementById('voice-button');
        voiceButton.addEventListener('mousedown', () => this.startRecording());
        voiceButton.addEventListener('mouseup', () => this.stopRecording());
        voiceButton.addEventListener('mouseleave', () => this.stopRecording());
        voiceButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        voiceButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        // Configuraciones
        document.getElementById('ai-provider').addEventListener('change', (e) => {
            this.settings.aiProvider = e.target.value;
            this.saveSettings();
            this.updateAIProvider();
        });

        document.getElementById('voice-enabled').addEventListener('change', (e) => {
            this.settings.voiceEnabled = e.target.checked;
            this.saveSettings();
        });

        document.getElementById('auto-play').addEventListener('change', (e) => {
            this.settings.autoPlay = e.target.checked;
            this.saveSettings();
        });

        document.getElementById('language-input').addEventListener('change', (e) => {
            this.settings.languageInput = e.target.value;
            this.saveSettings();
        });

        const voiceSpeedSlider = document.getElementById('voice-speed');
        voiceSpeedSlider.addEventListener('input', (e) => {
            this.settings.voiceSpeed = parseFloat(e.target.value);
            document.getElementById('voice-speed-value').textContent = `${this.settings.voiceSpeed}x`;
            this.saveSettings();
        });

        // Menú contextual
        document.addEventListener('contextmenu', (e) => this.showContextMenu(e));
        document.addEventListener('click', () => this.hideContextMenu());
    }

    updateUI() {
        // Actualizar controles con configuraciones guardadas
        document.getElementById('ai-provider').value = this.settings.aiProvider;
        document.getElementById('voice-enabled').checked = this.settings.voiceEnabled;
        document.getElementById('auto-play').checked = this.settings.autoPlay;
        document.getElementById('language-input').value = this.settings.languageInput;
        document.getElementById('voice-speed').value = this.settings.voiceSpeed;
        document.getElementById('voice-speed-value').textContent = `${this.settings.voiceSpeed}x`;

        // Actualizar estado del botón de voz
        const voiceToggle = document.getElementById('voice-toggle');
        if (this.settings.voiceEnabled) {
            voiceToggle.classList.add('active');
            voiceToggle.querySelector('i').className = 'fas fa-volume-up';
        } else {
            voiceToggle.classList.remove('active');
            voiceToggle.querySelector('i').className = 'fas fa-volume-mute';
        }
    }

    setupTextareaResize() {
        const textarea = document.getElementById('message-input');
        textarea.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });
    }

    updateCharCounter() {
        const messageInput = document.getElementById('message-input');
        const charCount = document.getElementById('char-count');
        charCount.textContent = messageInput.value.length;

        // Habilitar/deshabilitar botón de envío
        const sendButton = document.getElementById('send-button');
        sendButton.disabled = messageInput.value.trim().length === 0;
    }

    async checkStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();

            const statusIndicator = document.querySelector('.status-indicator .fa-circle');
            const backendStatus = document.getElementById('backend-status');

            if (status.services.backend === 'online') {
                statusIndicator.style.color = 'var(--success-color)';
                backendStatus.textContent = 'Conectado';
                backendStatus.style.color = 'var(--success-color)';
            } else {
                statusIndicator.style.color = 'var(--error-color)';
                backendStatus.textContent = 'Desconectado';
                backendStatus.style.color = 'var(--error-color)';
            }
        } catch (error) {
            console.error('Error al verificar estado:', error);
            const statusIndicator = document.querySelector('.status-indicator .fa-circle');
            const backendStatus = document.getElementById('backend-status');
            statusIndicator.style.color = 'var(--error-color)';
            backendStatus.textContent = 'Error';
            backendStatus.style.color = 'var(--error-color)';
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();

        if (!message) return;

        // Agregar mensaje del usuario
        this.addMessage(message, 'user');
        messageInput.value = '';
        messageInput.style.height = 'auto';
        this.updateCharCounter();

        // Mostrar indicador de escritura
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.chatHistory
                })
            });

            const data = await response.json();

            this.hideTypingIndicator();

            if (data.error) {
                this.addMessage(`Error: ${data.error}`, 'ai', true);
                this.showNotification('Error al procesar mensaje', 'error');
                return;
            }

            // Agregar respuesta de la IA
            const messageId = this.addMessage(data.response, 'ai');

            // Actualizar historial
            this.chatHistory = data.history || [];

            // Generar audio si está habilitado
            if (this.settings.voiceEnabled) {
                this.generateAudio(data.response, messageId);
            }

            // Mostrar información del proveedor
            this.showProviderInfo(data.provider, data.model);

        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            this.hideTypingIndicator();
            this.addMessage('Error de conexión. Por favor, intenta de nuevo.', 'ai', true);
            this.showNotification('Error de conexión', 'error');
        }
    }

    addMessage(content, type, isError = false) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message-container ${type}-message`;
        messageDiv.dataset.messageId = messageId;

        const currentTime = new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${type === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble ${isError ? 'error' : ''}">
                    <p>${this.formatMessage(content)}</p>
                </div>
                <div class="message-meta">
                    <span class="message-time">${currentTime}</span>
                    ${type === 'ai' && !isError ? '<button class="play-audio" style="display: none;"><i class="fas fa-play"></i></button>' : ''}
                </div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return messageId;
    }

    formatMessage(message) {
        // Formatear mensajes con HTML básico
        return message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    showTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'block';

        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'none';
    }

    async startRecording() {
        if (this.isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };

            this.mediaRecorder.start();
            this.isRecording = true;

            // Actualizar UI
            const voiceButton = document.getElementById('voice-button');
            voiceButton.classList.add('recording');

            const recordingStatus = document.getElementById('recording-status');
            recordingStatus.style.display = 'block';

            this.startRecordingTimer();

        } catch (error) {
            console.error('Error al acceder al micrófono:', error);
            this.showNotification('Error al acceder al micrófono', 'error');
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;

        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        this.isRecording = false;

        // Actualizar UI
        const voiceButton = document.getElementById('voice-button');
        voiceButton.classList.remove('recording');

        const recordingStatus = document.getElementById('recording-status');
        recordingStatus.style.display = 'none';

        this.stopRecordingTimer();
    }

    startRecordingTimer() {
        this.recordingStartTime = Date.now();
        this.recordingTimer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('recording-time').textContent =
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopRecordingTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
    }

    async processRecording() {
        if (this.audioChunks.length === 0) return;

        this.showLoading('Procesando audio...');

        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('language', this.settings.languageInput);

            const response = await fetch('/api/chat/audio-to-text', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            this.hideLoading();

            if (data.error) {
                this.showNotification(`Error: ${data.error}`, 'error');
                return;
            }

            // Insertar texto transcrito en el input
            const messageInput = document.getElementById('message-input');
            messageInput.value = data.transcript;
            messageInput.focus();
            this.updateCharCounter();

            // Auto-enviar si hay texto
            if (data.transcript.trim()) {
                setTimeout(() => this.sendMessage(), 500);
            }

        } catch (error) {
            console.error('Error al procesar audio:', error);
            this.hideLoading();
            this.showNotification('Error al procesar audio', 'error');
        }
    }

    async generateAudio(text, messageId) {
        try {
            const response = await fetch('/api/chat/text-to-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    language: 'es',
                    voice_id: 'speaker_es_f01'
                })
            });

            const data = await response.json();

            if (data.error) {
                console.error('Error al generar audio:', data.error);
                return;
            }

            // Mostrar botón de reproducir audio
            const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                const playButton = messageElement.querySelector('.play-audio');
                if (playButton) {
                    playButton.style.display = 'inline-block';
                    playButton.dataset.audioUrl = data.audio_url || '';
                    playButton.dataset.audioBase64 = data.audio_base64 || '';

                    playButton.addEventListener('click', () => this.playAudio(playButton));

                    // Auto-reproducir si está habilitado
                    if (this.settings.autoPlay) {
                        setTimeout(() => this.playAudio(playButton), 500);
                    }
                }
            }

        } catch (error) {
            console.error('Error al generar audio:', error);
        }
    }

    playAudio(button) {
        const audioPlayer = document.getElementById('audio-player');
        const audioUrl = button.dataset.audioUrl;
        const audioBase64 = button.dataset.audioBase64;

        if (audioUrl) {
            audioPlayer.src = audioUrl;
        } else if (audioBase64) {
            audioPlayer.src = `data:audio/wav;base64,${audioBase64}`;
        } else {
            this.showNotification('Audio no disponible', 'warning');
            return;
        }

        audioPlayer.playbackRate = this.settings.voiceSpeed;

        // Cambiar icono mientras reproduce
        const icon = button.querySelector('i');
        const originalClass = icon.className;

        audioPlayer.onplay = () => {
            icon.className = 'fas fa-pause';
        };

        audioPlayer.onended = () => {
            icon.className = originalClass;
        };

        audioPlayer.onerror = () => {
            icon.className = originalClass;
            this.showNotification('Error al reproducir audio', 'error');
        };

        if (audioPlayer.paused) {
            audioPlayer.play();
        } else {
            audioPlayer.pause();
            icon.className = originalClass;
        }
    }

    clearChat() {
        if (confirm('¿Estás seguro de que quieres limpiar la conversación?')) {
            const messagesContainer = document.getElementById('chat-messages');
            messagesContainer.innerHTML = `
                <div class="message-container ai-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-bubble">
                            <p>¡Hola! Soy tu asistente de IA. Puedes escribir tu mensaje o usar el micrófono para hablar conmigo. ¿En qué puedo ayudarte hoy?</p>
                        </div>
                        <div class="message-meta">
                            <span class="message-time">Ahora</span>
                        </div>
                    </div>
                </div>
            `;

            this.chatHistory = [];
            this.showNotification('Conversación limpiada', 'success');
        }
    }

    toggleVoice() {
        this.settings.voiceEnabled = !this.settings.voiceEnabled;
        this.saveSettings();
        this.updateUI();

        const status = this.settings.voiceEnabled ? 'activadas' : 'desactivadas';
        this.showNotification(`Respuestas por voz ${status}`, 'info');
    }

    toggleSettings() {
        const settingsPanel = document.getElementById('settings-panel');
        settingsPanel.classList.toggle('active');
    }

    async updateAIProvider() {
        try {
            const response = await fetch('/api/chat/set-provider', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    provider: this.settings.aiProvider,
                    api_key: '', // Se puede implementar input para API key
                    model: this.getModelForProvider(this.settings.aiProvider)
                })
            });

            const data = await response.json();

            if (data.error) {
                this.showNotification(`Error: ${data.error}`, 'error');
                return;
            }

            this.showNotification(`Proveedor cambiado a ${data.provider}`, 'success');
            this.showProviderInfo(data.provider, data.model);

        } catch (error) {
            console.error('Error al cambiar proveedor:', error);
            this.showNotification('Error al cambiar proveedor', 'error');
        }
    }

    getModelForProvider(provider) {
        const models = {
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-sonnet',
            'huggingface': 'microsoft/DialoGPT-medium',
            'deepseek-local': 'deepseek-r1-8b',
            'fallback': 'demo'
        };
        return models[provider] || 'unknown';
    }

    showProviderInfo(provider, model) {
        const chatStatus = document.getElementById('chat-status');
        const providerNames = {
            'openai': 'OpenAI GPT',
            'anthropic': 'Anthropic Claude',
            'huggingface': 'Hugging Face',
            'deepseek-local': 'DeepSeek R1 (Local)',
            'fallback': 'Demo'
        };

        const providerName = providerNames[provider] || provider;
        chatStatus.innerHTML = `
            <span class="status-indicator online"></span>
            ${providerName} - ${model}
        `;
    }

    showContextMenu(event) {
        const messageElement = event.target.closest('.message-container');
        if (!messageElement) return;

        event.preventDefault();

        const contextMenu = document.getElementById('context-menu');
        const messageText = messageElement.querySelector('.message-bubble p').textContent;
        const isAIMessage = messageElement.classList.contains('ai-message');

        // Mostrar/ocultar opciones específicas para mensajes de IA
        const aiOnlyItems = contextMenu.querySelectorAll('.ai-only');
        aiOnlyItems.forEach(item => {
            item.style.display = isAIMessage ? 'block' : 'none';
        });

        contextMenu.style.display = 'block';
        contextMenu.style.left = event.pageX + 'px';
        contextMenu.style.top = event.pageY + 'px';

        // Remover listeners anteriores
        const items = contextMenu.querySelectorAll('li');
        items.forEach(item => {
            item.replaceWith(item.cloneNode(true));
        });

        // Agregar nuevos listeners
        contextMenu.querySelector('[data-action="copy"]').addEventListener('click', () => {
            navigator.clipboard.writeText(messageText);
            this.showNotification('Texto copiado', 'success');
            this.hideContextMenu();
        });

        contextMenu.querySelector('[data-action="speak"]').addEventListener('click', () => {
            const playButton = messageElement.querySelector('.play-audio');
            if (playButton && playButton.style.display !== 'none') {
                this.playAudio(playButton);
            } else {
                // Generar audio si no existe
                const messageId = messageElement.dataset.messageId;
                this.generateAudio(messageText, messageId);
            }
            this.hideContextMenu();
        });

        if (isAIMessage) {
            contextMenu.querySelector('[data-action="regenerate"]').addEventListener('click', () => {
                // Obtener el mensaje anterior del usuario para regenerar
                const prevUserMessage = this.getLastUserMessage();
                if (prevUserMessage) {
                    this.regenerateResponse(prevUserMessage);
                }
                this.hideContextMenu();
            });
        }
    }

    hideContextMenu() {
        const contextMenu = document.getElementById('context-menu');
        contextMenu.style.display = 'none';
    }

    getLastUserMessage() {
        const userMessages = document.querySelectorAll('.message-container.user-message');
        const lastUserMessage = userMessages[userMessages.length - 1];
        return lastUserMessage ? lastUserMessage.querySelector('.message-bubble p').textContent : null;
    }

    async regenerateResponse(userMessage) {
        // Remover la última respuesta de la IA
        const aiMessages = document.querySelectorAll('.message-container.ai-message');
        const lastAIMessage = aiMessages[aiMessages.length - 1];
        if (lastAIMessage) {
            lastAIMessage.remove();
        }

        // Regenerar respuesta
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    history: this.chatHistory.slice(0, -1) // Remover última respuesta del historial
                })
            });

            const data = await response.json();
            this.hideTypingIndicator();

            if (data.error) {
                this.addMessage(`Error: ${data.error}`, 'ai', true);
                return;
            }

            const messageId = this.addMessage(data.response, 'ai');
            this.chatHistory = data.history || [];

            if (this.settings.voiceEnabled) {
                this.generateAudio(data.response, messageId);
            }

        } catch (error) {
            console.error('Error al regenerar respuesta:', error);
            this.hideTypingIndicator();
            this.addMessage('Error al regenerar respuesta', 'ai', true);
        }
    }

    showLoading(message = 'Procesando...') {
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        loadingText.textContent = message;
        loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        loadingOverlay.style.display = 'none';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;

        const container = document.getElementById('notification-container');
        container.appendChild(notification);

        // Auto-remover después de 3 segundos
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }
}

// Inicializar chat cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new VokaFlowChat();
});
