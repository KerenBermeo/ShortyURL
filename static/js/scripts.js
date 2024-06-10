document.getElementById('shortenForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const urlInput = document.getElementById('url_input');
    const originalUrl = urlInput.value;
    const dataToSend = { url: originalUrl };

    fetch('/shorten', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {

        // Limpiar cualquier URL acortada previamente
        const existingShortUrlContainer = document.querySelector('.short-url');
        if (existingShortUrlContainer) {
            existingShortUrlContainer.remove();
        }
        // Crear un nuevo elemento de tipo <div>
        const shortUrlContainer = document.createElement('div');

        // Asignar la dirección corta como el texto del elemento
        shortUrlContainer.textContent = `Short URL: ${data.short_url}`;

        // Agregar la clase CSS al elemento
        shortUrlContainer.classList.add('short-url');

        // Agregar un evento de clic para redirigir al usuario a la dirección original
        shortUrlContainer.addEventListener('click', () => {
            window.location.href = data.original_url;
        });

        // Agregar el elemento al DOM, debajo del formulario
        document.getElementById('shortenForm').appendChild(shortUrlContainer);
        
    })
    .catch(error => {
        console.error('Error:', error);
    });
});



