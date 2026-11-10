import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App';

afterEach(() => {
  jest.restoreAllMocks();
});

test('renders assistant title, backend selector, and default Hugging Face model', () => {
  render(<App />);
  expect(screen.getByText(/Local Multi-Model AI Assistant/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Backend/i)).toHaveValue('huggingface');
  expect(screen.getByLabelText(/Model/i)).toHaveValue('flan-t5');
});

test('switching backend to Ollama updates the model list to Mistral', () => {
  render(<App />);
  const backendSelect = screen.getByLabelText(/Backend/i);
  fireEvent.change(backendSelect, { target: { value: 'ollama' } });

  expect(backendSelect).toHaveValue('ollama');
  expect(screen.getByLabelText(/Model/i)).toHaveValue('mistral:latest');
});

test('submitting a prompt sends a POST request to /generate and displays the response', async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          response: 'Hello from local Flan-T5!',
          backend: 'huggingface',
          model: 'flan-t5',
        }),
    })
  );

  render(<App />);
  const input = screen.getByLabelText(/Prompt/i);
  const sendButton = screen.getByRole('button', { name: /Send/i });

  fireEvent.change(input, { target: { value: 'Explain local AI' } });
  fireEvent.click(sendButton);

  await waitFor(() => {
    expect(screen.getByText('Hello from local Flan-T5!')).toBeInTheDocument();
  });

  expect(global.fetch).toHaveBeenCalledWith(
    'http://127.0.0.1:5001/generate',
    expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({
        message: 'Explain local AI',
        model: 'flan-t5',
        backend: 'huggingface',
      }),
    })
  );
});
