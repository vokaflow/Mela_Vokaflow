/* ================================================
   VokaFlow WebApp - JavaScript de la Página de Inicio
   ================================================ */

// Inicialización de la página de inicio
document.addEventListener('DOMContentLoaded', function () {
    Logger.info('Index page initialized');

    // Inicializar animaciones
    initializeAnimations();

    // Cargar estado del sistema
    loadSystemStatus();

    // Configurar interacciones
    setupInteractions();

    // Verificar estado del sistema automáticamente
    setInterval(loadSystemStatus, 60000); // Cada minuto
});

// Configurar animaciones de entrada
function initializeAnimations() {
    // Observador de intersección para animaciones al scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observar elementos que deben animarse
    const animatedElements = document.querySelectorAll(
        '.feature-card, .capability, .action-btn'
    );

    animatedElements.forEach(el => {
        observer.observe(el);
    });

    // Animación del contador en las estadísticas
    animateCounters();
}

// Animar contadores numérticos
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');

    counters.forEach(counter => {
        const target = counter.textContent.trim();

        // Solo animar números
        if (/^\d+/.test(target)) {
            const number = parseInt(target);
            animateNumber(counter, 0, number, 2000);
        }
    });
}

// Animar un número desde start hasta end
function animateNumber(element, start, end, duration) {
    const startTime = performance.now();

    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function (ease out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (end - start) * easeOut);

        element.textContent = current + (element.textContent.includes('+') ? '+' : '');

        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }

    requestAnimationFrame(updateNumber);
}

// Cargar y mostrar estado del sistema
async function loadSystemStatus() {
    try {
        const status = await SystemStatus.check();

        if (status) {
            updateStatusDisplay(status);
        }
    } catch (error) {
        Logger.error('Error loading system status:', error);
    }
}

// Actualizar visualización del estado
function updateStatusDisplay(status) {
    // Actualizar estado del backend
    const backendStatus = document.getElementById('backend-status-value');
    if (backendStatus) {
        const isOnline = status.services?.backend === 'online';
        backendStatus.innerHTML = `
            <i class="fas fa-circle" style="color: ${isOnline ? 'var(--success-color)' : 'var(--error-color)'}"></i>
            ${isOnline ? 'Online' : 'Offline'}
        `;
        backendStatus.className = `status-value ${isOnline ? 'online' : 'offline'}`;
    }

    // Actualizar estado de IA
    const aiStatus = document.getElementById('ai-status-value');
    if (aiStatus) {
        const isConfigured = status.services?.ai_configured;
        aiStatus.innerHTML = `
            <i class="fas fa-circle" style="color: ${isConfigured ? 'var(--success-color)' : 'var(--warning-color)'}"></i>
            ${isConfigured ? 'Configurada' : 'Sin configurar'}
        `;
        aiStatus.className = `status-value ${isConfigured ? 'online' : 'offline'}`;
    }

    // Actualizar estado de funcionalidades
    const featuresStatus = document.getElementById('features-status-value');
    if (featuresStatus) {
        const features = status.features || {};
        const activeFeatures = Object.values(features).filter(Boolean).length;
        const totalFeatures = Object.keys(features).length;

        featuresStatus.innerHTML = `
            <i class="fas fa-cog" style="color: var(--primary-color)"></i>
            ${activeFeatures}/${totalFeatures} activas
        `;
        featuresStatus.className = 'status-value online';
    }
}

// Configurar interacciones de la página
function setupInteractions() {
    // Configurar botones de acción rápida
    setupQuickActions();

    // Configurar cards de características
    setupFeatureCards();

    // Configurar traducciones populares
    setupPopularTranslations();
}

// Configurar acciones rápidas
function setupQuickActions() {
    const actionButtons = document.querySelectorAll('.action-btn');

    actionButtons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-3px) scale(1.02)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = '';
        });
    });
}

// Configurar cards de características
function setupFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');

    featureCards.forEach(card => {
        // Efecto parallax sutil en el movimiento del mouse
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });

        // Efecto de click
        card.addEventListener('click', (e) => {
            // Si el click no es en el botón, navegar a la página
            if (!e.target.closest('.feature-button')) {
                const button = card.querySelector('.feature-button');
                if (button) {
                    button.click();
                }
            }
        });
    });
}

// Configurar traducciones populares (si existen en la página)
function setupPopularTranslations() {
    const popularItems = document.querySelectorAll('.popular-item');

    popularItems.forEach(item => {
        item.addEventListener('click', () => {
            const source = item.dataset.source;
            const sourceLang = item.dataset.sourceLang;
            const targetLang = item.dataset.targetLang;

            // Redirigir al traductor con parámetros
            const params = new URLSearchParams({
                text: source,
                from: sourceLang,
                to: targetLang
            });

            window.location.href = `/translator?${params.toString()}`;
        });

        // Efecto hover
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateY(-2px)';
            item.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
        });

        item.addEventListener('mouseleave', () => {
            item.style.transform = '';
            item.style.boxShadow = '';
        });
    });
}

// Funciones globales para los botones de acción
window.navigateToChat = function () {
    window.location.href = '/chat';
};

window.navigateToTranslator = function () {
    window.location.href = '/translator';
};

// Función para probar conectividad con el backend
window.testBackendConnection = async function () {
    Loading.show('Probando conexión con el backend...');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        Loading.hide();

        if (response.ok) {
            Notifications.success('Conexión con el backend exitosa');
            updateStatusDisplay(data);
        } else {
            Notifications.error('Error al conectar con el backend');
        }
    } catch (error) {
        Loading.hide();
        Logger.error('Backend connection test failed:', error);
        Notifications.error('No se pudo conectar con el backend');
    }
};

// Función para mostrar detalles del sistema
window.showSystemDetails = function () {
    const modal = createSystemModal();
    document.body.appendChild(modal);

    // Centrar y mostrar el modal
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
};

// Crear modal con detalles del sistema
function createSystemModal() {
    const modal = document.createElement('div');
    modal.className = 'system-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="this.parentElement.remove()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3>Detalles del Sistema</h3>
                <button class="modal-close" onclick="this.closest('.system-modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="system-info">
                    <h4>Configuración</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Versión:</label>
                            <span>${VokaFlow.version}</span>
                        </div>
                        <div class="info-item">
                            <label>Backend URL:</label>
                            <span>${VokaFlow.backendUrl}</span>
                        </div>
                        <div class="info-item">
                            <label>Debug:</label>
                            <span>${VokaFlow.debug ? 'Activado' : 'Desactivado'}</span>
                        </div>
                        <div class="info-item">
                            <label>Navegador:</label>
                            <span>${navigator.userAgent.split(' ')[0]}</span>
                        </div>
                    </div>
                    
                    <h4>Capacidades del Navegador</h4>
                    <div class="capabilities-list">
                        <div class="capability-item ${AudioRecorder.isSupported() ? 'supported' : 'not-supported'}">
                            <i class="fas fa-microphone"></i>
                            <span>Grabación de Audio</span>
                            <i class="fas ${AudioRecorder.isSupported() ? 'fa-check text-success' : 'fa-times text-error'}"></i>
                        </div>
                        <div class="capability-item ${navigator.clipboard ? 'supported' : 'not-supported'}">
                            <i class="fas fa-clipboard"></i>
                            <span>Portapapeles</span>
                            <i class="fas ${navigator.clipboard ? 'fa-check text-success' : 'fa-times text-error'}"></i>
                        </div>
                        <div class="capability-item ${navigator.serviceWorker ? 'supported' : 'not-supported'}">
                            <i class="fas fa-cog"></i>
                            <span>Service Worker</span>
                            <i class="fas ${navigator.serviceWorker ? 'fa-check text-success' : 'fa-times text-error'}"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.system-modal').remove()">
                    Cerrar
                </button>
                <button class="btn btn-primary" onclick="testBackendConnection()">
                    Probar Conexión
                </button>
            </div>
        </div>
    `;

    // Estilos del modal
    const style = document.createElement('style');
    style.textContent = `
        .system-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: var(--z-modal);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .system-modal.show {
            opacity: 1;
        }
        
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
        }
        
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--bg-card);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-xl);
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            padding: var(--spacing-lg);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: var(--font-size-lg);
            cursor: pointer;
            color: var(--text-secondary);
            padding: var(--spacing-xs);
        }
        
        .modal-body {
            padding: var(--spacing-lg);
        }
        
        .info-grid {
            display: grid;
            gap: var(--spacing-sm);
            margin-bottom: var(--spacing-lg);
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: var(--spacing-xs) 0;
        }
        
        .info-item label {
            font-weight: 500;
            color: var(--text-secondary);
        }
        
        .capabilities-list {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-sm);
        }
        
        .capability-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: var(--spacing-sm);
            background: var(--bg-secondary);
            border-radius: var(--border-radius);
        }
        
        .capability-item i:first-child {
            color: var(--primary-color);
        }
        
        .capability-item span {
            flex: 1;
        }
        
        .modal-footer {
            padding: var(--spacing-lg);
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: var(--spacing-sm);
            justify-content: flex-end;
        }
    `;

    modal.appendChild(style);
    return modal;
}

// Agregar CSS para animaciones
const animationStyle = document.createElement('style');
animationStyle.textContent = `
    .animate-in {
        animation: slideInUp 0.6s ease-out forwards;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .feature-card, .capability, .action-btn {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease-out;
    }
`;

document.head.appendChild(animationStyle);
