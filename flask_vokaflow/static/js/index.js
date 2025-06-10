/* ================================================
   VokaFlow - Página Principal - JavaScript
   ================================================ */

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    Logger.info('VokaFlow Index Page loaded');

    // Inicializar animaciones
    initAnimations();

    // Configurar eventos interactivos
    bindEvents();

    // Verificar estado del sistema
    checkInitialStatus();
});

function initAnimations() {
    // Animación de contador de estadísticas
    animateStats();

    // Animación de elementos flotantes
    enhanceFloatingElements();

    // Intersección observada para animaciones on-scroll
    setupScrollAnimations();
}

function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');

    const animateNumber = (element, target, duration = 2000) => {
        const start = 0;
        const startTime = performance.now();

        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Función de easing
            const easeOut = 1 - Math.pow(1 - progress, 3);

            if (target.includes('+')) {
                const num = parseInt(target.replace('+', ''));
                const current = Math.floor(easeOut * num);
                element.textContent = current + '+';
            } else if (target.includes('%')) {
                const num = parseFloat(target.replace('%', ''));
                const current = (easeOut * num).toFixed(1);
                element.textContent = current + '%';
            } else if (target.includes('<')) {
                // Para "&lt;1s"
                element.textContent = target;
            } else if (target.includes('/')) {
                // Para "24/7"
                element.textContent = target;
            } else {
                const num = parseInt(target);
                const current = Math.floor(easeOut * num);
                element.textContent = current;
            }

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };

        requestAnimationFrame(updateNumber);
    };

    // Observer para cuando las estadísticas sean visibles
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target.textContent;
                animateNumber(entry.target, target);
                statsObserver.unobserve(entry.target);
            }
        });
    });

    statNumbers.forEach(stat => {
        statsObserver.observe(stat);
    });
}

function enhanceFloatingElements() {
    const floatingElements = document.querySelectorAll('.floating-element');

    floatingElements.forEach((element, index) => {
        // Agregar tooltip con el texto
        const text = element.dataset.text;
        if (text) {
            element.setAttribute('title', text);
        }

        // Agregar interactividad
        element.addEventListener('mouseenter', () => {
            element.style.transform = 'scale(1.1)';
            element.style.background = 'rgba(255, 255, 255, 0.25)';
        });

        element.addEventListener('mouseleave', () => {
            element.style.transform = 'scale(1)';
            element.style.background = 'rgba(255, 255, 255, 0.15)';
        });
    });
}

function setupScrollAnimations() {
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
    const animateElements = document.querySelectorAll('.feature-card, .tech-item, .diagram-node');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

function bindEvents() {
    // Botones de navegación con animación
    const navButtons = document.querySelectorAll('.hero-actions .btn');
    navButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Agregar efecto visual
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 150);
        });
    });

    // Enlaces de características con seguimiento
    const featureLinks = document.querySelectorAll('.feature-link');
    featureLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const feature = link.closest('.feature-card').querySelector('h3').textContent;
            Logger.info(`Feature clicked: ${feature}`);
        });
    });

    // Nodos del diagrama tecnológico con información
    const diagramNodes = document.querySelectorAll('.diagram-node');
    diagramNodes.forEach(node => {
        const tech = node.dataset.tech;

        node.addEventListener('mouseenter', () => {
            showTechInfo(node, tech);
        });

        node.addEventListener('mouseleave', () => {
            hideTechInfo();
        });
    });
}

function showTechInfo(node, tech) {
    // Crear tooltip temporal
    const tooltip = document.createElement('div');
    tooltip.className = 'tech-tooltip';
    tooltip.style.cssText = `
        position: absolute;
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
        border: 1px solid var(--border-color);
    `;

    const techDescriptions = {
        'IA': 'Inteligencia Artificial Avanzada',
        'STT': 'Speech-to-Text (Voz a Texto)',
        'TTS': 'Text-to-Speech (Texto a Voz)',
        'Traducción': 'Traducción Multi-idioma'
    };

    tooltip.textContent = techDescriptions[tech] || tech;

    const rect = node.getBoundingClientRect();
    tooltip.style.left = (rect.left + rect.width / 2) + 'px';
    tooltip.style.top = (rect.bottom + 10) + 'px';
    tooltip.style.transform = 'translateX(-50%)';

    document.body.appendChild(tooltip);

    // Animar entrada
    setTimeout(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateX(-50%) translateY(0)';
    }, 10);
}

function hideTechInfo() {
    const tooltip = document.querySelector('.tech-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

async function checkInitialStatus() {
    try {
        const status = await SystemStatus.check();

        if (status && status.services.backend === 'online') {
            Logger.info('Backend conectado correctamente');

            // Mostrar notificación de bienvenida
            setTimeout(() => {
                Notifications.success('¡Bienvenido a VokaFlow! Sistema listo para usar.', 4000);
            }, 1000);
        } else {
            Logger.warn('Backend desconectado');

            // Mostrar información sobre modo demo
            setTimeout(() => {
                Notifications.info('Ejecutándose en modo demo. Algunas funciones pueden estar limitadas.', 6000);
            }, 1500);
        }
    } catch (error) {
        Logger.error('Error verificando estado inicial:', error);
    }
}

// Funciones globales para botones de la página
window.startChat = function () {
    Logger.info('Navigating to chat...');
    window.location.href = '/chat';
};

window.startTranslator = function () {
    Logger.info('Navigating to translator...');
    window.location.href = '/translator';
};

window.scrollToFeatures = function () {
    const featuresSection = document.querySelector('.features-section');
    if (featuresSection) {
        featuresSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
};

// Demo de características
window.demoChat = function () {
    Logger.info('Chat demo requested');

    Notifications.info('Dirigiéndote al chat inteligente...', 2000);

    setTimeout(() => {
        window.location.href = '/chat';
    }, 1000);
};

window.demoTranslator = function () {
    Logger.info('Translator demo requested');

    Notifications.info('Abriendo el traductor universal...', 2000);

    setTimeout(() => {
        window.location.href = '/translator';
    }, 1000);
};

// Efectos visuales adicionales
function addVisualEffects() {
    // Parallax suave en hero
    let lastScrollTop = 0;

    window.addEventListener('scroll', Utils.throttle(() => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollDirection = scrollTop > lastScrollTop ? 'down' : 'up';

        // Efecto parallax en elementos del hero
        const heroVisual = document.querySelector('.hero-visual');
        if (heroVisual && scrollTop < window.innerHeight) {
            const offset = scrollTop * 0.3;
            heroVisual.style.transform = `translateY(${offset}px)`;
        }

        lastScrollTop = scrollTop;
    }, 10));
}

// CSS adicional para animaciones
const additionalStyles = `
    .feature-card, .tech-item {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease-out;
    }
    
    .feature-card.animate-in, .tech-item.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .diagram-node {
        transition: all 0.3s ease;
    }
    
    .diagram-node:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 20px 40px rgba(59, 130, 246, 0.3);
    }
    
    .tech-tooltip {
        opacity: 0;
        transform: translateX(-50%) translateY(-10px);
        transition: all 0.2s ease;
    }
`;

// Agregar estilos adicionales
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Inicializar efectos visuales
setTimeout(addVisualEffects, 500);

// Actualizar indicadores cada 30 segundos
setInterval(() => {
    SystemStatus.check();
}, 30000);

Logger.info('VokaFlow Index JavaScript initialized');
