const chatbox = document.getElementById('chatbox');
const form = document.getElementById('chat-form');
const textInput = document.getElementById('text-input');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name');

function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.className = sender;
    div.textContent = (sender === 'user' ? 'You: ' : 'Bot: ') + text;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
} 

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    fileNameDisplay.textContent = `Selected file: ${fileInput.files[0].name}`;
  } else {
    fileNameDisplay.textContent = '';
  }
});

// Handle Enter key in text area
textInput.addEventListener('keydown', function (event) {
    // Pressing Enter without Shift will submit
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent newline
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
});

form.addEventListener('submit', async e => {
    e.preventDefault();

    const message = textInput.value.trim();
    const file = fileInput.files[0];

    if (!message && !file) {
        appendMessage("Please enter a message or upload a file.", 'bot');
        return;
    }

    appendMessage(message || file.name, 'user');

    const formData = new FormData();
    if (message) formData.append('text', message);
    if (file) formData.append('file', file);

    try {
        const res = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        appendMessage(data.response, 'bot');

    } catch (err) {
        appendMessage("Error processing your request.", 'bot');
    }

    // Clear input fields
    textInput.value = '';
    fileInput.value = '';
    fileNameDisplay.textContent = '';  // <-- Clear the displayed file name here
});
