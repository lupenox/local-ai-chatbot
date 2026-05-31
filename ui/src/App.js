import { useState } from 'react';
import './App.css';

const modelOptions = {
  huggingface: [
    { id: 'flan-t5', label: 'Flan-T5 Small' },
    { id: 'distil-gpt2', label: 'DistilGPT-2' },
    { id: 'tiny-llama', label: 'TinyLlama' },
    { id: 'phi-2', label: 'Phi-2' },
    { id: 'gpt2', label: 'GPT-2' },
  ],
  ollama: [
    { id: 'mistral:latest', label: 'Mistral' },
    { id: 'deepseek-coder:latest', label: 'DeepSeek Coder' },
  ],
};

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Local AI Assistant is ready. Choose a backend, select a model, and send a prompt to run local inference.',
    },
  ]);
  const [input, setInput] = useState('');
  const [selectedBackend, setSelectedBackend] = useState('huggingface');
  const [selectedModel, setSelectedModel] = useState('flan-t5');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  function changeBackend(event) {
    const backend = event.target.value;
    setSelectedBackend(backend);
    setSelectedModel(modelOptions[backend][0].id);
  }

  async function sendMessage(event) {
    event.preventDefault();

    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    const userMessage = { role: 'user', text: trimmedInput };
    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setInput('');
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5001/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: trimmedInput,
          model: selectedModel,
          backend: selectedBackend,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'The local model service returned an error.');
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          text: data.response || 'No response generated.',
        },
      ]);
    } catch (requestError) {
      const errorMessage = requestError.message || 'Could not reach the local Flask service.';
      setError(errorMessage);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          text: 'I could not connect to the local model service. Make sure ai_service.py is running on port 5001 and Ollama is running if you selected the Ollama backend.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">Privacy-first local inference</p>
        <h1>Local Multi-Model AI Assistant</h1>
        <p className="hero-copy">
          Desktop chatbot prototype powered by Flask, Hugging Face Transformers, PyTorch,
          Ollama, Electron, and optional voice interaction workflows.
        </p>
        <div className="status-grid">
          <span>Flask API</span>
          <span>HF + Ollama</span>
          <span>Offline-First</span>
          <span>Speech Ready</span>
        </div>
      </section>

      <section className="chat-panel" aria-label="Local AI chat interface">
        <div className="chat-header">
          <div>
            <p className="eyebrow">Model Console</p>
            <h2>Chat Session</h2>
          </div>
          <div className="model-controls">
            <label className="model-picker">
              Backend
              <select value={selectedBackend} onChange={changeBackend}>
                <option value="huggingface">Hugging Face</option>
                <option value="ollama">Ollama</option>
              </select>
            </label>
            <label className="model-picker">
              Model
              <select value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
                {modelOptions[selectedBackend].map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="messages" aria-live="polite">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
              <span className="message-role">{message.role === 'user' ? 'You' : 'Assistant'}</span>
              <p>{message.text}</p>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <span className="message-role">Assistant</span>
              <p>Generating locally with {selectedBackend} / {selectedModel}...</p>
            </div>
          )}
        </div>

        {error && <p className="error-message">{error}</p>}

        <form className="prompt-form" onSubmit={sendMessage}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask the local assistant something..."
            aria-label="Prompt"
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? 'Running' : 'Send'}
          </button>
        </form>
      </section>
    </main>
  );
}

export default App;
