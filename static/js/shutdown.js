/**
 * Funcionalidad para el botón de apagado seguro
 */
document.addEventListener('DOMContentLoaded', function() {
    // Crear el botón de apagado y añadirlo a la página
    const shutdownButton = document.createElement('button');
    shutdownButton.className = 'shutdown-button';
    shutdownButton.id = 'shutdownButton';
    shutdownButton.textContent = 'Apagar Servidor';
    
    // Crear modal de confirmación
    const shutdownModal = document.createElement('div');
    shutdownModal.className = 'shutdown-modal';
    shutdownModal.id = 'shutdownModal';
    shutdownModal.innerHTML = `
        <div class="shutdown-modal-content">
            <h2 class="shutdown-modal-title">¿Estás seguro?</h2>
            <p>Esta acción apagará el servidor VokaFlow. Todos los procesos en curso se detendrán.</p>
            <div class="shutdown-modal-buttons">
                <button class="shutdown-modal-button confirm" id="confirmShutdown">Confirmar Apagado</button>
                <button class="shutdown-modal-button cancel" id="cancelShutdown">Cancelar</button>
            </div>
        </div>
    `;
    
    // Añadir elementos al DOM
    const headerElement = document.querySelector('header');
    if (headerElement) {
        headerElement.appendChild(shutdownButton);
        document.body.appendChild(shutdownModal);
        
        // Configurar eventos
        shutdownButton.addEventListener('click', function() {
            shutdownModal.classList.add('active');
        });
        
        document.getElementById('cancelShutdown').addEventListener('click', function() {
            shutdownModal.classList.remove('active');
        });
        
        document.getElementById('confirmShutdown').addEventListener('click', function() {
            // Hacer la petición para apagar el servidor
            shutdownServer();
        });
    }
});

/**
 * Realiza la petición al servidor para apagarlo
 */
function shutdownServer() {
    const confirmButton = document.getElementById('confirmShutdown');
    const cancelButton = document.getElementById('cancelShutdown');
    const modalContent = document.querySelector('.shutdown-modal-content');
    
    // Deshabilitar botones durante la petición
    confirmButton.disabled = true;
    cancelButton.disabled = true;
    confirmButton.textContent = 'Apagando...';
    
    // Realizar petición
    fetch('/api/system/shutdown', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Error al intentar apagar el servidor');
    })
    .then(data => {
        // Mostrar mensaje de éxito
        modalContent.innerHTML = `
            <h2 class="shutdown-modal-title" style="color: #4caf50;">Apagado Iniciado</h2>
            <p>${data.message}</p>
            <p>El servidor se está apagando de forma segura...</p>
            <p>Puedes cerrar esta ventana.</p>
        `;
        
        // Cambiar el estado del botón
        const shutdownButton = document.getElementById('shutdownButton');
        if (shutdownButton) {
            shutdownButton.textContent = 'Servidor Apagándose...';
            shutdownButton.disabled = true;
            shutdownButton.classList.add('confirming');
        }
    })
    .catch(error => {
        // Mostrar mensaje de error
        modalContent.innerHTML = `
            <h2 class="shutdown-modal-title" style="color: #FF5252;">Error</h2>
            <p>${error.message}</p>
            <div class="shutdown-modal-buttons">
                <button class="shutdown-modal-button cancel" id="closeErrorModal">Cerrar</button>
            </div>
        `;
        
        // Configurar evento para cerrar modal
        document.getElementById('closeErrorModal').addEventListener('click', function() {
            document.getElementById('shutdownModal').classList.remove('active');
        });
    });
} 