/**
 * Power Menu Checker - Garantiza que el menú de energía esté presente y funcional
 */
(function() {
    // Esperar a que el DOM esté completamente cargado
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Power Checker: Verificando menú de energía...');
        
        // Darle tiempo a que el script principal cargue
        setTimeout(checkPowerMenu, 2000);
        
        function checkPowerMenu() {
            // Verificar si el botón de energía existe
            const powerButton = document.getElementById('powerButton');
            const powerMenu = document.querySelector('.power-menu');
            
            if (!powerButton || !powerMenu) {
                console.warn('Power Checker: No se encontró el menú de energía, intentando recrearlo...');
                createPowerMenu();
            } else {
                console.log('Power Checker: Menú de energía verificado correctamente');
                // Asegurarse de que sea visible
                powerMenu.style.display = 'block';
                powerButton.style.display = 'flex';
                powerButton.style.opacity = '1';
                powerButton.classList.add('power-button-visible');
            }
        }
        
        function createPowerMenu() {
            // Comprobar si ya existe el script principal
            const scriptExists = Array.from(document.scripts).some(script => 
                script.src && script.src.includes('power_menu.js'));
                
            if (!scriptExists) {
                console.log('Power Checker: Cargando script de menú de energía...');
                // Cargar el script principal
                const script = document.createElement('script');
                script.src = '/static/js/power_menu.js';
                document.head.appendChild(script);
            } else {
                // El script existe pero no funcionó, intentar crear manualmente el menú
                console.log('Power Checker: Creando menú de energía manualmente...');
                
                // Crear estructura del menú de energía
                const powerMenu = document.createElement('div');
                powerMenu.className = 'power-menu';
                powerMenu.style.display = 'block';
                powerMenu.innerHTML = `
                    <div class="power-button power-button-visible" id="powerButton" style="display: flex; opacity: 1;"></div>
                    <div class="power-menu-options" id="powerMenuOptions">
                        <button class="power-menu-option shutdown" id="shutdownOption">
                            <span class="power-icon shutdown"></span>Apagar
                        </button>
                        <button class="power-menu-option restart" id="restartOption">
                            <span class="power-icon restart"></span>Reiniciar
                        </button>
                        <button class="power-menu-option hibernate" id="hibernateOption">
                            <span class="power-icon hibernate"></span>Hibernar
                        </button>
                    </div>
                `;
                
                // Crear modal de confirmación
                const confirmModal = document.createElement('div');
                confirmModal.className = 'power-confirm-modal';
                confirmModal.id = 'powerConfirmModal';
                confirmModal.innerHTML = `
                    <div class="power-confirm-content" id="powerConfirmContent">
                        <h2 class="power-confirm-title" id="powerConfirmTitle">Confirmar acción</h2>
                        <p class="power-confirm-message" id="powerConfirmMessage">¿Estás seguro de que quieres realizar esta acción?</p>
                        <div class="power-confirm-buttons">
                            <button class="power-confirm-button confirm" id="powerConfirmButton">Confirmar</button>
                            <button class="power-confirm-button cancel" id="powerCancelButton">Cancelar</button>
                        </div>
                    </div>
                `;
                
                // Añadir elementos al DOM
                document.body.appendChild(powerMenu);
                document.body.appendChild(confirmModal);
                
                // Configurar eventos básicos
                const powerButton = document.getElementById('powerButton');
                const powerMenuOptions = document.getElementById('powerMenuOptions');
                
                if (powerButton && powerMenuOptions) {
                    powerButton.addEventListener('click', function() {
                        powerMenuOptions.classList.toggle('active');
                    });
                    
                    document.addEventListener('click', function(event) {
                        if (!powerMenu.contains(event.target)) {
                            powerMenuOptions.classList.remove('active');
                        }
                    });
                }
                
                // Aplicar eventos de opciones del menú
                setupPowerMenuEvents();
            }
        }
        
        function setupPowerMenuEvents() {
            // Configurar eventos para cada opción
            const shutdownOption = document.getElementById('shutdownOption');
            const restartOption = document.getElementById('restartOption');
            const hibernateOption = document.getElementById('hibernateOption');
            const powerConfirmButton = document.getElementById('powerConfirmButton');
            const powerCancelButton = document.getElementById('powerCancelButton');
            const powerConfirmModal = document.getElementById('powerConfirmModal');
            
            if (!shutdownOption || !restartOption || !hibernateOption || 
                !powerConfirmButton || !powerCancelButton || !powerConfirmModal) {
                console.error('Power Checker: No se pudieron encontrar todos los elementos necesarios');
                return;
            }
            
            let currentAction = '';
            
            function showConfirmation(action) {
                currentAction = action;
                document.getElementById('powerMenuOptions').classList.remove('active');
                
                // Configurar título y mensaje según la acción
                let title, message;
                
                switch (action) {
                    case 'shutdown':
                        title = 'Confirmar apagado';
                        message = '¿Estás seguro de que quieres apagar el servidor VokaFlow? Todos los procesos en curso se detendrán.';
                        break;
                    case 'restart':
                        title = 'Confirmar reinicio';
                        message = '¿Estás seguro de que quieres reiniciar el servidor VokaFlow? El servicio estará momentáneamente no disponible.';
                        break;
                    case 'hibernate':
                        title = 'Confirmar hibernación';
                        message = '¿Estás seguro de que quieres hibernar el servidor VokaFlow? Los procesos se pausarán y se podrán reanudar más tarde.';
                        break;
                }
                
                document.getElementById('powerConfirmTitle').textContent = title;
                document.getElementById('powerConfirmMessage').textContent = message;
                powerConfirmModal.classList.add('active');
            }
            
            function executeAction(action) {
                // Deshabilitar botones durante la petición
                powerConfirmButton.disabled = true;
                powerCancelButton.disabled = true;
                powerConfirmButton.textContent = 'Procesando...';
                
                // Endpoint y mensaje según la acción
                let endpoint, successTitle, successMessage;
                
                // Obtener la URL base actual
                const baseUrl = window.location.origin;
                
                switch (action) {
                    case 'shutdown':
                        endpoint = `${baseUrl}/api/system/shutdown`;
                        successTitle = 'Apagado iniciado';
                        successMessage = 'El servidor se está apagando de forma segura...';
                        break;
                    case 'restart':
                        endpoint = `${baseUrl}/api/system/restart`;
                        successTitle = 'Reinicio iniciado';
                        successMessage = 'El servidor se está reiniciando...';
                        break;
                    case 'hibernate':
                        endpoint = `${baseUrl}/api/system/hibernate`;
                        successTitle = 'Hibernación iniciada';
                        successMessage = 'El servidor se está preparando para hibernar...';
                        break;
                }
                
                console.log(`Power Checker: Enviando petición a: ${endpoint}`);
                
                // Realizar petición con manejo de errores mejorado
                fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    // Añadir un timeout para evitar esperas indefinidas
                    signal: AbortSignal.timeout(10000) // 10 segundos timeout
                })
                .then(response => {
                    console.log(`Power Checker: Respuesta recibida: ${response.status} ${response.statusText}`);
                    
                    if (!response.ok) {
                        if (response.status === 404) {
                            throw new Error(`API no encontrada (404): La ruta ${endpoint} no existe`);
                        } else if (response.status === 401 || response.status === 403) {
                            throw new Error(`Error de autorización: No tiene permisos para realizar esta acción`);
                        } else {
                            throw new Error(`Error de servidor: ${response.status}`);
                        }
                    }
                    
                    return response.json().catch(() => {
                        // Si no es JSON, devolver un objeto con un mensaje
                        console.warn('Power Checker: La respuesta no es un JSON válido');
                        return { message: 'Operación completada, pero la respuesta no es un JSON válido' };
                    });
                })
                .then(data => {
                    console.log('Power Checker: Datos recibidos:', data);
                    
                    // Mostrar mensaje de éxito
                    document.getElementById('powerConfirmContent').innerHTML = `
                        <h2 class="power-confirm-title" style="color: #4caf50;">${successTitle}</h2>
                        <p>${data.message || 'Operación completada con éxito'}</p>
                        <p>${successMessage}</p>
                        <button class="power-confirm-button cancel" id="closeSuccessModal">Cerrar</button>
                    `;
                    
                    // Configurar evento para cerrar modal
                    document.getElementById('closeSuccessModal').addEventListener('click', function() {
                        powerConfirmModal.classList.remove('active');
                    });
                    
                    // Deshabilitar el botón de energía temporalmente
                    const powerButton = document.getElementById('powerButton');
                    powerButton.style.opacity = '0.5';
                    powerButton.style.pointerEvents = 'none';
                    
                    // Volver a habilitar después de un tiempo
                    if (action !== 'shutdown') {
                        setTimeout(() => {
                            powerButton.style.opacity = '1';
                            powerButton.style.pointerEvents = 'auto';
                        }, 30000); // 30 segundos
                    }
                })
                .catch(error => {
                    console.error(`Power Checker: Error al ejecutar la acción ${action}:`, error);
                    
                    // Intentar una alternativa con URLs relativas si el error es 404
                    if (error.message.includes('404') && endpoint.startsWith(baseUrl)) {
                        console.log('Power Checker: Intentando URL relativa como alternativa...');
                        
                        let relativeEndpoint;
                        switch (action) {
                            case 'shutdown': relativeEndpoint = '/api/system/shutdown'; break;
                            case 'restart': relativeEndpoint = '/api/system/restart'; break;
                            case 'hibernate': relativeEndpoint = '/api/system/hibernate'; break;
                        }
                        
                        // Mostrar mensaje de reintento
                        document.getElementById('powerConfirmContent').innerHTML = `
                            <h2 class="power-confirm-title" style="color: #FFA700;">Reintentando...</h2>
                            <p>Se produjo un error con la URL absoluta. Intentando con URL relativa.</p>
                            <div class="power-confirm-buttons">
                                <button class="power-confirm-button cancel" id="closeErrorModal">Cancelar</button>
                            </div>
                        `;
                        
                        // Configurar evento para cerrar modal
                        document.getElementById('closeErrorModal').addEventListener('click', function() {
                            powerConfirmModal.classList.remove('active');
                            powerConfirmButton.disabled = false;
                            powerCancelButton.disabled = false;
                            powerConfirmButton.textContent = 'Confirmar';
                        });
                        
                        // Intentar con URL relativa después de un segundo
                        setTimeout(() => {
                            fetch(relativeEndpoint, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Accept': 'application/json'
                                },
                                signal: AbortSignal.timeout(10000)
                            })
                            .then(response => {
                                console.log(`Power Checker: Respuesta de reintento: ${response.status} ${response.statusText}`);
                                if (!response.ok) {
                                    throw new Error(`Error en el reintento: ${response.status}`);
                                }
                                return response.json().catch(() => ({ message: 'Operación completada en el reintento' }));
                            })
                            .then(data => {
                                document.getElementById('powerConfirmContent').innerHTML = `
                                    <h2 class="power-confirm-title" style="color: #4caf50;">${successTitle}</h2>
                                    <p>${data.message || 'Operación completada con éxito'}</p>
                                    <p>${successMessage}</p>
                                    <button class="power-confirm-button cancel" id="closeSuccessModal">Cerrar</button>
                                `;
                                
                                document.getElementById('closeSuccessModal').addEventListener('click', function() {
                                    powerConfirmModal.classList.remove('active');
                                });
                                
                                const powerButton = document.getElementById('powerButton');
                                powerButton.style.opacity = '0.5';
                                powerButton.style.pointerEvents = 'none';
                                
                                if (action !== 'shutdown') {
                                    setTimeout(() => {
                                        powerButton.style.opacity = '1';
                                        powerButton.style.pointerEvents = 'auto';
                                    }, 30000);
                                }
                            })
                            .catch(retryError => {
                                console.error(`Power Checker: Error en el reintento:`, retryError);
                                showFinalErrorMessage(action, retryError);
                            });
                        }, 1000);
                        
                        return;
                    }
                    
                    // Mostrar mensaje de error final
                    showFinalErrorMessage(action, error);
                });
            }
            
            function showFinalErrorMessage(action, error) {
                document.getElementById('powerConfirmContent').innerHTML = `
                    <h2 class="power-confirm-title" style="color: #FF5252;">Error</h2>
                    <p>Error al intentar ${action === 'shutdown' ? 'apagar' : action === 'restart' ? 'reiniciar' : 'hibernar'} el servidor.</p>
                    <p>Detalles: ${error.message}</p>
                    <p class="debug-info">Comprueba la consola del navegador para más detalles.</p>
                    <div class="power-confirm-buttons">
                        <button class="power-confirm-button cancel" id="closeErrorModal">Cerrar</button>
                    </div>
                `;
                
                // Configurar evento para cerrar modal
                document.getElementById('closeErrorModal').addEventListener('click', function() {
                    powerConfirmModal.classList.remove('active');
                    
                    // Re-habilitar los botones
                    powerConfirmButton.disabled = false;
                    powerCancelButton.disabled = false;
                    powerConfirmButton.textContent = 'Confirmar';
                });
            }
            
            shutdownOption.addEventListener('click', function() { showConfirmation('shutdown'); });
            restartOption.addEventListener('click', function() { showConfirmation('restart'); });
            hibernateOption.addEventListener('click', function() { showConfirmation('hibernate'); });
            
            // Cancelar acción
            powerCancelButton.addEventListener('click', function() {
                powerConfirmModal.classList.remove('active');
            });
            
            // Confirmar acción
            powerConfirmButton.addEventListener('click', function() {
                executeAction(currentAction);
            });
        }
    });
    
    // También verificar después de que la página se haya cargado completamente
    window.addEventListener('load', function() {
        setTimeout(function() {
            const powerButton = document.getElementById('powerButton');
            if (powerButton) {
                powerButton.classList.add('power-button-visible');
                console.log('Power Checker: Visibilidad del botón de energía reforzada después de carga completa');
            }
        }, 3000);
    });
})(); 