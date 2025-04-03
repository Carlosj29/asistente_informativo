let detectedText = ""; // Variable global para almacenar el contenido del documento

// Función para manejar la respuesta del asistente y reproducir el audio
function handleResponse(response) {
    const audioPlayer = document.getElementById('audioPlayer');
    
    // Configurar el audio desde el base64 recibido
    const audioData = "data:audio/mp3;base64," + response.audio;
    audioPlayer.src = audioData;

    // Reproducir el audio
    audioPlayer.style.display = 'block';
    audioPlayer.play();
    
    // Mostrar la respuesta en el área correspondiente
    document.getElementById('explanation').textContent = response.response;
}

// Manejo de la subida de archivo
document.getElementById('uploadBtn').addEventListener('click', function() {
    const fileInput = document.getElementById('fileInput');
    fileInput.click();
});

// Cuando se selecciona un archivo
document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Mostrar un loader mientras procesamos el archivo
        const loader = document.getElementById('loader');
        loader.style.display = 'block';

        // Subir el archivo al backend
        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loader.style.display = 'none'; // Ocultar loader
            detectedText = data.content; // Guardar el contenido extraído del archivo
            document.getElementById('detectedText').textContent = detectedText;
            document.getElementById('questionSection').style.display = 'block'; // Mostrar la sección de preguntas
        })
        .catch(error => {
            loader.style.display = 'none'; // Ocultar loader
            console.error('Error:', error);
        });
    }
});

// Cuando se hace una pregunta
document.getElementById('askButton').addEventListener('click', function() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    
    if (question) {
        // Limpiar el campo de pregunta
        questionInput.value = '';

        // Mostrar un loader mientras se obtiene la respuesta
        const loader = document.getElementById('loader');
        loader.style.display = 'block';

        // Llamar al backend para obtener la respuesta
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                document: detectedText // El contenido extraído del archivo
            }),
        })
        .then(response => response.json())
        .then(data => {
            loader.style.display = 'none'; // Ocultar loader

            // Manejar la respuesta y reproducir el audio
            handleResponse(data);
        })
        .catch(error => {
            loader.style.display = 'none'; // Ocultar loader
            console.error('Error:', error);
        });
    }
});