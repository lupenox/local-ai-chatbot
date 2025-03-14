// renderer.js

document.getElementById('send-btn').addEventListener('click', async () => {
    const userInput = document.getElementById('user-input').value.trim();
    const selectedModel = document.getElementById('model-select').value;
    const responseElement = document.getElementById('ai-response');
    const loadingElement = document.getElementById('loading');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');

    if (!userInput) {
        responseElement.textContent = "⚠️ Please enter a message.";
        return;
    }

    // Show loading spinner and progress bar
    loadingElement.style.display = 'block';
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    responseElement.textContent = "";

    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += 10;
            progressBar.style.width = progress + '%';
        }
    }, 300);

    try {
        const res = await fetch('/generate', {

            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: userInput,
                model: selectedModel
            })
        });

        const data = await res.json();

        if (data.response) {
            responseElement.textContent = data.response;
        } else if (data.error) {
            responseElement.textContent = `⚠️ Error: ${data.error}`;
        } else {
            responseElement.textContent = "⚠️ Unexpected error occurred.";
        }

    } catch (error) {
        responseElement.textContent = `⚠️ Request failed: ${error.message}`;
    } finally {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        setTimeout(() => {
            loadingElement.style.display = 'none';
            progressContainer.style.display = 'none';
        }, 500);
    }
});
