document.getElementById('shortenForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const urlInput = document.getElementById('url_input');
    const originalUrl = urlInput.value;
    const dataToSend = { url: originalUrl };

    console.log('Original URL:', originalUrl); // Para verificar el valor de la URL capturada

    fetch('/shorten', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => {
        console.log('Response status:', response.status); // Para verificar el estado de la respuesta
        console.log('Response body:', response.body); // Para verificar el cuerpo de la respuesta
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Data from server:', data); // Para verificar los datos devueltos por el servidor

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



