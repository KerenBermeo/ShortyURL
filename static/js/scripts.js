document.addEventListener('DOMContentLoaded', function() {
    // Forms
    const shortenForm = document.getElementById('shortenForm');
    const statsForm = document.getElementById('statsForm');
    
    // Result containers
    const resultContainer = document.getElementById('resultContainer');
    const statsContainer = document.getElementById('statsContainer');
    
    // Botón de copiar
    const copyBtn = document.getElementById('copyBtn');
    
    // Validación de formularios con Bootstrap
    Array.from(document.querySelectorAll('.needs-validation')).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Acortar URL
    shortenForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (!shortenForm.checkValidity()) return;
        
        const urlInput = document.getElementById('url_input');
        const url = urlInput.value.trim();
        
        try {
            const response = await fetch('/shorten', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': 'tu_clave_api' // Reemplaza con tu clave API real
                },
                body: JSON.stringify({ url })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const shortUrlElement = document.getElementById('shortUrl');
                shortUrlElement.value = data.short_url;
                
                // Mostrar resultado
                resultContainer.classList.remove('d-none');
                
                // Scroll suave al resultado
                resultContainer.scrollIntoView({ behavior: 'smooth' });
                
                // Resetear formulario
                shortenForm.reset();
                shortenForm.classList.remove('was-validated');
            } else {
                throw new Error(data.error || 'Error al acortar la URL');
            }
        } catch (error) {
            showAlert('Error', error.message, 'danger');
            console.error('Error:', error);
        }
    });
    
    // Copiar URL al portapapeles
    copyBtn.addEventListener('click', function() {
        const shortUrl = document.getElementById('shortUrl').value;
        
        navigator.clipboard.writeText(shortUrl)
            .then(() => {
                // Cambiar icono temporalmente
                const icon = copyBtn.querySelector('i');
                icon.classList.remove('bi-clipboard');
                icon.classList.add('bi-check2');
                
                // Restaurar después de 2 segundos
                setTimeout(() => {
                    icon.classList.remove('bi-check2');
                    icon.classList.add('bi-clipboard');
                }, 2000);
            })
            .catch(err => {
                console.error('Error al copiar:', err);
                showAlert('Error', 'No se pudo copiar la URL', 'danger');
            });
    });
    
    // Consultar estadísticas
    statsForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (!statsForm.checkValidity()) return;
        
        const shortUrlInput = document.getElementById('short_url_input');
        const shortUrl = shortUrlInput.value.trim();
        
        // Extraer el short_id de la URL
        const shortId = shortUrl.split('/').pop();
        
        try {
            const response = await fetch(`/stats/${shortId}`, {
                headers: {
                    'X-API-KEY': 'tu_clave_api' // Reemplaza con tu clave API real
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Mostrar estadísticas
                document.getElementById('originalUrl').textContent = data.original_url;
                document.getElementById('originalUrl').href = data.original_url;
                document.getElementById('createdAt').textContent = formatDate(data.stats.created_at);
                document.getElementById('lastAccessed').textContent = data.stats.last_accessed ? formatDate(data.stats.last_accessed) : 'Nunca';
                document.getElementById('totalClicks').textContent = data.stats.total_clicks;
                
                statsContainer.classList.remove('d-none');
                
                // Scroll suave a las estadísticas
                statsContainer.scrollIntoView({ behavior: 'smooth' });
                
                // Resetear formulario
                statsForm.reset();
                statsForm.classList.remove('was-validated');
            } else {
                throw new Error(data.error || 'Error al obtener estadísticas');
            }
        } catch (error) {
            showAlert('Error', error.message, 'danger');
            console.error('Error:', error);
        }
    });
    
    // Función para mostrar alertas
    function showAlert(title, message, type) {
        const alertPlaceholder = document.createElement('div');
        alertPlaceholder.innerHTML = [
            `<div class="alert alert-${type} alert-dismissible fade show" role="alert">`,
            `   <strong>${title}</strong> ${message}`,
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'
        ].join('');
        
        document.body.prepend(alertPlaceholder);
        
        // Auto cerrar después de 5 segundos
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(alertPlaceholder.querySelector('.alert'));
            alert.close();
        }, 5000);
    }
    
    // Formatear fecha
    function formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        };
        return new Date(dateString).toLocaleDateString('es-ES', options);
    }
});