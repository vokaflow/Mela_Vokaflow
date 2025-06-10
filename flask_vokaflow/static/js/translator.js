/* ================================================
   VokaFlow - Traductor Universal - JavaScript
   ================================================ */

class VokaFlowTranslator {
    constructor() {
        this.translationHistory = [];
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentAudioUrl = null;
        this.settings = {
            autoDetect: true,
            rememberLanguages: true,
            showConfidence: true,
            autoSave: false
        };

        this.languages = {
            'auto': 'Detectar idioma',
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'ar': 'العربية',
            'hi': 'हिन्दी',
            'tr': 'Türkçe',
            'nl': 'Nederlands',
            'sv': 'Svenska'
        };

        this.init();
    }

    init() {
        this.loadSettings();
        this.loadHistory();
        this.bindEvents();
        this.updateUI();
        this.setupLanguageNames();

        console.log('VokaFlow Translator inicializado');
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('vokaflow_translator_settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
    }

    saveSettings() {
        localStorage.setItem('vokaflow_translator_settings', JSON.stringify(this.settings));
    }

    loadHistory() {
        const savedHistory = localStorage.getItem('vokaflow_translator_history');
        if (savedHistory) {
            this.translationHistory = JSON.parse(savedHistory);
            this.updateHistoryDisplay();
        }
    }

    saveHistory() {
        // Mantener solo las últimas 50 traducciones
        if (this.translationHistory.length > 50) {
            this.translationHistory = this.translationHistory.slice(-50);
        }
        localStorage.setItem('vokaflow_translator_history', JSON.stringify(this.translationHistory));
        this.updateHistoryDisplay();
    }

    bindEvents() {
        // Botones principales
        document.getElementById('translate-button').addEventListener('click', () => this.translateText());
        document.getElementById('translate-audio-button').addEventListener('click', () => this.translateAudio());
        document.getElementById('swap-languages').addEventListener('click', () => this.swapLanguages());

        // Selectores de idioma
        document.getElementById('source-language').addEventListener('change', () => this.updateLanguageNames());
        document.getElementById('target-language').addEventListener('change', () => this.updateLanguageNames());

        // Botones de panel
        document.getElementById('source-voice-button').addEventListener('mousedown', () => this.startRecording());
        document.getElementById('source-voice-button').addEventListener('mouseup', () => this.stopRecording());
        document.getElementById('source-voice-button').addEventListener('mouseleave', () => this.stopRecording());
        document.getElementById('source-voice-button').addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        document.getElementById('source-voice-button').addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        document.getElementById('source-clear').addEventListener('click', () => this.clearSourceText());
        document.getElementById('target-copy').addEventListener('click', () => this.copyTranslation());
        document.getElementById('target-speak').addEventListener('click', () => this.speakTranslation());
        document.getElementById('target-share').addEventListener('click', () => this.shareTranslation());

        // Área de texto
        const sourceText = document.getElementById('source-text');
        sourceText.addEventListener('input', () => this.updateCharCounter());
        sourceText.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.translateText();
            }
        });

        // Acciones rápidas
        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', (e) => this.handleQuickAction(e.currentTarget.dataset.action));
        });

        // Traducciones populares
        document.querySelectorAll('.popular-item').forEach(item => {
            item.addEventListener('click', () => this.loadPopularTranslation(item));
        });

        // Historial
        document.getElementById('clear-history').addEventListener('click', () => this.clearHistory());

        // Auto-traducir mientras escribe (con debounce)
        let translateTimeout;
        sourceText.addEventListener('input', () => {
            clearTimeout(translateTimeout);
            const text = sourceText.value.trim();
            if (text.length > 0) {
                translateTimeout = setTimeout(() => {
                    this.translateText();
                }, 1500); // Esperar 1.5 segundos después de dejar de escribir
            }
        });
    }

    updateUI() {
        this.updateCharCounter();
        this.updateLanguageNames();

        // Actualizar el botón de traducir
        const translateButton = document.getElementById('translate-button');
        const sourceText = document.getElementById('source-text').value.trim();
        translateButton.disabled = sourceText.length === 0;
    }

    setupLanguageNames() {
        // Actualizar nombres de idiomas en los selectores si es necesario
        const sourceSelect = document.getElementById('source-language');
        const targetSelect = document.getElementById('target-language');

        // Los options ya están en el HTML, solo actualizamos los nombres mostrados
        this.updateLanguageNames();
    }

    updateLanguageNames() {
        const sourceLanguage = document.getElementById('source-language').value;
        const targetLanguage = document.getElementById('target-language').value;

        document.getElementById('source-language-name').textContent = this.languages[sourceLanguage] || sourceLanguage;
        document.getElementById('target-language-name').textContent = this.languages[targetLanguage] || targetLanguage;
    }

    updateCharCounter() {
        const sourceText = document.getElementById('source-text');
        const charCount = document.getElementById('source-char-count');
        charCount.textContent = sourceText.value.length;

        // Habilitar/deshabilitar botón de traducir
        const translateButton = document.getElementById('translate-button');
        translateButton.disabled = sourceText.value.trim().length === 0;
    }

    swapLanguages() {
        const sourceSelect = document.getElementById('source-language');
        const targetSelect = document.getElementById('target-language');
        const sourceText = document.getElementById('source-text');
        const targetText = document.getElementById('target-text');

        // Intercambiar idiomas (evitar auto si está seleccionado)
        if (sourceSelect.value !== 'auto') {
            const tempLang = sourceSelect.value;
            sourceSelect.value = targetSelect.value;
            targetSelect.value = tempLang;
        }

        // Intercambiar textos si hay traducción
        const currentTranslation = targetText.textContent.trim();
        if (currentTranslation && !targetText.querySelector('.placeholder-text')) {
            sourceText.value = currentTranslation;
            this.clearTranslationResult();
            this.updateCharCounter();
            this.updateLanguageNames();

            // Auto-traducir el texto intercambiado
            setTimeout(() => this.translateText(), 500);
        } else {
            this.updateLanguageNames();
        }

        this.showToast('Idiomas intercambiados');
    }

    clearSourceText() {
        document.getElementById('source-text').value = '';
        this.clearTranslationResult();
        this.updateCharCounter();
        document.getElementById('source-text').focus();
    }

    clearTranslationResult() {
        const targetText = document.getElementById('target-text');
        targetText.innerHTML = `
            <div class="placeholder-text">
                <i class="fas fa-language"></i>
                <p>La traducción aparecerá aquí</p>
            </div>
        `;

        // Ocultar información adicional
        document.getElementById('confidence-info').style.display = 'none';
        document.getElementById('translation-info').style.display = 'none';
        document.getElementById('detected-info').style.display = 'none';
    }

    async translateText() {
        const sourceText = document.getElementById('source-text').value.trim();
        if (!sourceText) {
            this.showToast('Ingresa texto para traducir', 'warning');
            return;
        }

        const sourceLanguage = document.getElementById('source-language').value;
        const targetLanguage = document.getElementById('target-language').value;

        if (sourceLanguage === targetLanguage && sourceLanguage !== 'auto') {
            this.showToast('Los idiomas de origen y destino son iguales', 'warning');
            return;
        }

        this.showLoading();
        const startTime = Date.now();

        try {
            const response = await fetch('/api/translate/text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: sourceText,
                    source_lang: sourceLanguage,
                    target_lang: targetLanguage
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.error) {
                this.showToast(`Error: ${data.error}`, 'error');
                return;
            }

            const translationTime = ((Date.now() - startTime) / 1000).toFixed(1);
            this.displayTranslation(data, translationTime);
            this.addToHistory(sourceText, data, sourceLanguage, targetLanguage);

        } catch (error) {
            console.error('Error al traducir:', error);
            this.hideLoading();
            this.showToast('Error de conexión al traducir', 'error');
        }
    }

    displayTranslation(data, translationTime) {
        const targetText = document.getElementById('target-text');
        const confidenceInfo = document.getElementById('confidence-info');
        const translationInfo = document.getElementById('translation-info');
        const detectedInfo = document.getElementById('detected-info');

        // Mostrar traducción
        targetText.innerHTML = `<p>${this.formatText(data.translated_text)}</p>`;

        // Mostrar confianza si está disponible
        if (data.confidence !== undefined && this.settings.showConfidence) {
            const confidence = Math.round(data.confidence * 100);
            confidenceInfo.style.display = 'inline';
            document.getElementById('confidence-value').textContent = confidence;

            // Colorear según confianza
            const confidenceSpan = document.getElementById('confidence-value');
            if (confidence >= 90) {
                confidenceSpan.style.color = 'var(--confidence-high)';
            } else if (confidence >= 70) {
                confidenceSpan.style.color = 'var(--confidence-medium)';
            } else {
                confidenceSpan.style.color = 'var(--confidence-low)';
            }
        }

        // Mostrar idioma detectado si se usó auto-detección
        if (data.source_lang && data.source_lang !== document.getElementById('source-language').value) {
            detectedInfo.style.display = 'inline';
            document.getElementById('detected-language').textContent = this.languages[data.source_lang] || data.source_lang;
        }

        // Mostrar tiempo de traducción
        translationInfo.style.display = 'inline';
        document.getElementById('translation-time').textContent = translationTime;

        this.showToast('Texto traducido exitosamente', 'success');
    }

    formatText(text) {
        // Formatear texto básico manteniendo saltos de línea
        return text
            .replace(/\n/g, '<br>')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    async translateAudio() {
        const sourceText = document.getElementById('source-text').value.trim();
        if (!sourceText) {
            this.showToast('Primero traduce algún texto', 'warning');
            return;
        }

        // Si no hay traducción, traducir primero
        const targetText = document.getElementById('target-text');
        if (targetText.querySelector('.placeholder-text')) {
            await this.translateText();
            // Esperar un momento para que se complete la traducción
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        const translatedText = targetText.textContent.trim();
        if (!translatedText || targetText.querySelector('.placeholder-text')) {
            this.showToast('No hay traducción disponible para convertir a audio', 'warning');
            return;
        }

        this.showLoading('Generando audio...');

        try {
            const targetLanguage = document.getElementById('target-language').value;

            const response = await fetch('/api/chat/text-to-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: translatedText,
                    language: targetLanguage,
                    voice_id: this.getVoiceForLanguage(targetLanguage)
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.error) {
                this.showToast(`Error al generar audio: ${data.error}`, 'error');
                return;
            }

            // Reproducir audio
            this.playTranslationAudio(data);
            this.showToast('Audio generado exitosamente', 'success');

        } catch (error) {
            console.error('Error al generar audio:', error);
            this.hideLoading();
            this.showToast('Error de conexión al generar audio', 'error');
        }
    }

    getVoiceForLanguage(language) {
        const voices = {
            'es': 'speaker_es_f01',
            'en': 'speaker_en_f01',
            'fr': 'speaker_fr_f01',
            'de': 'speaker_de_f01',
            'it': 'speaker_it_f01',
            'pt': 'speaker_pt_f01'
        };
        return voices[language] || 'speaker_en_f01';
    }

    playTranslationAudio(audioData) {
        const audioPlayer = document.getElementById('audio-player');

        if (audioData.audio_url) {
            audioPlayer.src = audioData.audio_url;
        } else if (audioData.audio_base64) {
            audioPlayer.src = `data:audio/wav;base64,${audioData.audio_base64}`;
        } else {
            this.showToast('Audio no disponible', 'warning');
            return;
        }

        audioPlayer.onloadeddata = () => {
            audioPlayer.play().catch(error => {
                console.error('Error al reproducir audio:', error);
                this.showToast('Error al reproducir audio', 'error');
            });
        };

        audioPlayer.onerror = () => {
            this.showToast('Error al cargar audio', 'error');
        };
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
            const voiceButton = document.getElementById('source-voice-button');
            voiceButton.classList.add('recording');
            voiceButton.innerHTML = '<i class="fas fa-stop"></i>';

            const recordingIndicator = document.getElementById('source-recording');
            recordingIndicator.style.display = 'block';

            this.startRecordingTimer();

        } catch (error) {
            console.error('Error al acceder al micrófono:', error);
            this.showToast('Error al acceder al micrófono', 'error');
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;

        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        this.isRecording = false;

        // Actualizar UI
        const voiceButton = document.getElementById('source-voice-button');
        voiceButton.classList.remove('recording');
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';

        const recordingIndicator = document.getElementById('source-recording');
        recordingIndicator.style.display = 'none';

        this.stopRecordingTimer();
    }

    startRecordingTimer() {
        this.recordingStartTime = Date.now();
        this.recordingTimer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('source-recording-time').textContent =
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

            const sourceLanguage = document.getElementById('source-language').value;
            formData.append('language', sourceLanguage === 'auto' ? null : sourceLanguage);

            const response = await fetch('/api/chat/audio-to-text', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            this.hideLoading();

            if (data.error) {
                this.showToast(`Error: ${data.error}`, 'error');
                return;
            }

            // Insertar texto transcrito
            const sourceText = document.getElementById('source-text');
            sourceText.value = data.transcript;
            this.updateCharCounter();

            // Mostrar idioma detectado si es diferente
            if (data.language && data.language !== sourceLanguage) {
                const detectedInfo = document.getElementById('detected-info');
                detectedInfo.style.display = 'inline';
                document.getElementById('detected-language').textContent = this.languages[data.language] || data.language;
            }

            // Auto-traducir
            if (data.transcript.trim()) {
                setTimeout(() => this.translateText(), 500);
            }

            this.showToast('Audio transcrito exitosamente', 'success');

        } catch (error) {
            console.error('Error al procesar audio:', error);
            this.hideLoading();
            this.showToast('Error al procesar audio', 'error');
        }
    }

    copyTranslation() {
        const targetText = document.getElementById('target-text');
        const text = targetText.textContent.trim();

        if (!text || targetText.querySelector('.placeholder-text')) {
            this.showToast('No hay traducción para copiar', 'warning');
            return;
        }

        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Traducción copiada al portapapeles', 'success');
        }).catch(error => {
            console.error('Error al copiar:', error);
            this.showToast('Error al copiar texto', 'error');
        });
    }

    speakTranslation() {
        const targetText = document.getElementById('target-text');
        const text = targetText.textContent.trim();

        if (!text || targetText.querySelector('.placeholder-text')) {
            this.showToast('No hay traducción para reproducir', 'warning');
            return;
        }

        this.translateAudio();
    }

    shareTranslation() {
        const sourceText = document.getElementById('source-text').value.trim();
        const targetText = document.getElementById('target-text').textContent.trim();

        if (!sourceText || !targetText || document.getElementById('target-text').querySelector('.placeholder-text')) {
            this.showToast('No hay traducción para compartir', 'warning');
            return;
        }

        const sourceLanguage = document.getElementById('source-language-name').textContent;
        const targetLanguage = document.getElementById('target-language-name').textContent;

        const shareText = `🌐 Traducción VokaFlow\n\n` +
            `${sourceLanguage}: ${sourceText}\n` +
            `${targetLanguage}: ${targetText}\n\n` +
            `Traducido con VokaFlow`;

        if (navigator.share) {
            navigator.share({
                title: 'Traducción VokaFlow',
                text: shareText
            }).then(() => {
                this.showToast('Traducción compartida', 'success');
            }).catch(error => {
                console.error('Error al compartir:', error);
                this.fallbackShare(shareText);
            });
        } else {
            this.fallbackShare(shareText);
        }
    }

    fallbackShare(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Traducción copiada para compartir', 'success');
        }).catch(error => {
            console.error('Error al copiar para compartir:', error);
            this.showToast('Error al preparar para compartir', 'error');
        });
    }

    handleQuickAction(action) {
        switch (action) {
            case 'clear-all':
                this.clearAll();
                break;
            case 'copy-translation':
                this.copyTranslation();
                break;
            case 'save-translation':
                this.saveCurrentTranslation();
                break;
            case 'speak-both':
                this.speakBoth();
                break;
        }
    }

    clearAll() {
        if (confirm('¿Estás seguro de que quieres limpiar todo?')) {
            this.clearSourceText();
            this.clearTranslationResult();
            this.showToast('Todo limpiado', 'success');
        }
    }

    saveCurrentTranslation() {
        // Esta funcionalidad se puede expandir para guardar en un formato específico
        const sourceText = document.getElementById('source-text').value.trim();
        const targetText = document.getElementById('target-text').textContent.trim();

        if (!sourceText || !targetText || document.getElementById('target-text').querySelector('.placeholder-text')) {
            this.showToast('No hay traducción para guardar', 'warning');
            return;
        }

        // Por ahora, solo copiamos al portapapeles en formato JSON
        const translation = {
            source: sourceText,
            target: targetText,
            sourceLang: document.getElementById('source-language').value,
            targetLang: document.getElementById('target-language').value,
            timestamp: new Date().toISOString()
        };

        navigator.clipboard.writeText(JSON.stringify(translation, null, 2)).then(() => {
            this.showToast('Traducción guardada en portapapeles (JSON)', 'success');
        }).catch(error => {
            console.error('Error al guardar:', error);
            this.showToast('Error al guardar traducción', 'error');
        });
    }

    async speakBoth() {
        // Hablar primero el texto original, luego la traducción
        const sourceText = document.getElementById('source-text').value.trim();
        const targetText = document.getElementById('target-text').textContent.trim();

        if (!sourceText) {
            this.showToast('No hay texto para reproducir', 'warning');
            return;
        }

        this.showLoading('Generando audio...');

        try {
            // Generar audio del texto original
            const sourceLanguage = document.getElementById('source-language').value;
            const sourceResponse = await fetch('/api/chat/text-to-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: sourceText,
                    language: sourceLanguage === 'auto' ? 'es' : sourceLanguage,
                    voice_id: this.getVoiceForLanguage(sourceLanguage === 'auto' ? 'es' : sourceLanguage)
                })
            });

            const sourceAudioData = await sourceResponse.json();

            if (sourceAudioData.error) {
                this.hideLoading();
                this.showToast(`Error al generar audio original: ${sourceAudioData.error}`, 'error');
                return;
            }

            // Reproducir audio original
            await this.playAudioSequentially(sourceAudioData);

            // Si hay traducción, reproducir también
            if (targetText && !document.getElementById('target-text').querySelector('.placeholder-text')) {
                const targetLanguage = document.getElementById('target-language').value;
                const targetResponse = await fetch('/api/chat/text-to-audio', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: targetText,
                        language: targetLanguage,
                        voice_id: this.getVoiceForLanguage(targetLanguage)
                    })
                });

                const targetAudioData = await targetResponse.json();

                if (!targetAudioData.error) {
                    // Esperar un poco antes de reproducir la traducción
                    setTimeout(() => {
                        this.playAudioSequentially(targetAudioData);
                    }, 1000);
                }
            }

            this.hideLoading();
            this.showToast('Reproduciendo ambos audios', 'success');

        } catch (error) {
            console.error('Error al generar audio:', error);
            this.hideLoading();
            this.showToast('Error al generar audio', 'error');
        }
    }

    playAudioSequentially(audioData) {
        return new Promise((resolve, reject) => {
            const audioPlayer = document.getElementById('audio-player');

            if (audioData.audio_url) {
                audioPlayer.src = audioData.audio_url;
            } else if (audioData.audio_base64) {
                audioPlayer.src = `data:audio/wav;base64,${audioData.audio_base64}`;
            } else {
                reject(new Error('Audio no disponible'));
                return;
            }

            audioPlayer.onended = () => resolve();
            audioPlayer.onerror = () => reject(new Error('Error al reproducir audio'));

            audioPlayer.play().catch(reject);
        });
    }

    loadPopularTranslation(item) {
        const sourceText = item.dataset.source;
        const sourceLang = item.dataset.sourceLang;
        const targetLang = item.dataset.targetLang;

        document.getElementById('source-text').value = sourceText;
        document.getElementById('source-language').value = sourceLang;
        document.getElementById('target-language').value = targetLang;

        this.updateCharCounter();
        this.updateLanguageNames();
        this.clearTranslationResult();

        // Auto-traducir
        setTimeout(() => this.translateText(), 500);

        this.showToast('Traducción popular cargada', 'success');
    }

    addToHistory(sourceText, translationData, sourceLang, targetLang) {
        const historyItem = {
            id: Date.now(),
            sourceText: sourceText,
            translatedText: translationData.translated_text,
            sourceLang: sourceLang,
            targetLang: targetLang,
            confidence: translationData.confidence,
            timestamp: new Date().toISOString()
        };

        // Agregar al inicio del historial
        this.translationHistory.unshift(historyItem);
        this.saveHistory();
    }

    updateHistoryDisplay() {
        const historyContent = document.getElementById('history-content');

        if (this.translationHistory.length === 0) {
            historyContent.innerHTML = `
                <div class="history-empty">
                    <i class="fas fa-clock"></i>
                    <p>No hay traducciones recientes</p>
                </div>
            `;
            return;
        }

        const historyHTML = this.translationHistory.slice(0, 10).map(item => {
            const date = new Date(item.timestamp).toLocaleString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });

            return `
                <div class="history-item" data-id="${item.id}">
                    <div class="history-text">
                        <div class="history-source">
                            <strong>${this.languages[item.sourceLang] || item.sourceLang}:</strong>
                            ${item.sourceText}
                        </div>
                        <div class="history-target">
                            <strong>${this.languages[item.targetLang] || item.targetLang}:</strong>
                            ${item.translatedText}
                        </div>
                    </div>
                    <div class="history-meta">
                        <span class="history-time">${date}</span>
                        ${item.confidence ? `<span class="history-confidence">${Math.round(item.confidence * 100)}%</span>` : ''}
                    </div>
                    <div class="history-actions">
                        <button class="history-load" onclick="translator.loadFromHistory('${item.id}')">
                            <i class="fas fa-redo"></i>
                        </button>
                        <button class="history-delete" onclick="translator.deleteFromHistory('${item.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        historyContent.innerHTML = historyHTML;
    }

    loadFromHistory(itemId) {
        const item = this.translationHistory.find(h => h.id == itemId);
        if (!item) return;

        document.getElementById('source-text').value = item.sourceText;
        document.getElementById('source-language').value = item.sourceLang;
        document.getElementById('target-language').value = item.targetLang;

        this.updateCharCounter();
        this.updateLanguageNames();

        // Mostrar la traducción directamente
        const targetText = document.getElementById('target-text');
        targetText.innerHTML = `<p>${this.formatText(item.translatedText)}</p>`;

        this.showToast('Traducción cargada desde historial', 'success');
    }

    deleteFromHistory(itemId) {
        if (confirm('¿Eliminar esta traducción del historial?')) {
            this.translationHistory = this.translationHistory.filter(h => h.id != itemId);
            this.saveHistory();
            this.showToast('Traducción eliminada del historial', 'success');
        }
    }

    clearHistory() {
        if (confirm('¿Estás seguro de que quieres limpiar todo el historial?')) {
            this.translationHistory = [];
            this.saveHistory();
            this.showToast('Historial limpiado', 'success');
        }
    }

    showLoading(message = 'Traduciendo...') {
        const loadingOverlay = document.getElementById('translation-loading');
        const loadingText = loadingOverlay.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
        loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('translation-loading');
        loadingOverlay.style.display = 'none';
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('success-toast');
        const toastMessage = document.getElementById('toast-message');

        toastMessage.textContent = message;

        // Cambiar color según tipo
        if (type === 'error') {
            toast.style.background = 'var(--error-color)';
        } else if (type === 'warning') {
            toast.style.background = 'var(--warning-color)';
        } else if (type === 'info') {
            toast.style.background = 'var(--accent-color)';
        } else {
            toast.style.background = 'var(--success-color)';
        }

        toast.style.display = 'flex';

        // Auto-ocultar después de 3 segundos
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }
}

// Variable global para acceso desde HTML
let translator;

// Inicializar traductor cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    translator = new VokaFlowTranslator();
});
