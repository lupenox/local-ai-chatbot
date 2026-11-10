import unittest
from unittest.mock import MagicMock, patch

import requests
import torch

import ai_service
import wake


class FakeInputs(dict):
    def to(self, _device):
        return self


class AIServiceTests(unittest.TestCase):
    def setUp(self):
        ai_service.model_cache.clear()
        self.client = ai_service.app.test_client()

    def test_health_endpoint_returns_service_metadata(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "running")
        self.assertIn("huggingface", payload["backends"])
        self.assertIn("ollama", payload["backends"])

    def test_generate_rejects_empty_message(self):
        response = self.client.post("/generate", json={"message": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.get_json()["error"].lower())

    def test_generate_rejects_unknown_backend(self):
        response = self.client.post(
            "/generate",
            json={"message": "Hello", "backend": "unknown-backend"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid backend", response.get_json()["error"])

    def test_generate_rejects_invalid_huggingface_model(self):
        response = self.client.post(
            "/generate",
            json={"message": "Hello", "backend": "huggingface", "model": "not-a-model"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid Hugging Face model", response.get_json()["error"])

    def test_generate_with_huggingface_seq2seq_caches_model(self):
        fake_tokenizer = MagicMock()
        fake_tokenizer.pad_token_id = 0
        fake_tokenizer.return_value = FakeInputs({"input_ids": torch.tensor([[1, 2, 3]])})
        fake_tokenizer.decode.return_value = "Seq2Seq answer"

        fake_model = MagicMock()
        fake_model.to.return_value = fake_model
        fake_model.generate.return_value = torch.tensor([[10, 11, 12]])

        with (
            patch.object(ai_service.AutoTokenizer, "from_pretrained", return_value=fake_tokenizer) as mock_tok,
            patch.object(ai_service.AutoModelForSeq2SeqLM, "from_pretrained", return_value=fake_model) as mock_cls,
        ):
            first = self.client.post(
                "/generate",
                json={"message": "Summarize this", "backend": "huggingface", "model": "flan-t5"},
            )
            second = self.client.post(
                "/generate",
                json={"message": "Summarize again", "backend": "huggingface", "model": "flan-t5"},
            )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["response"], "Seq2Seq answer")
        self.assertEqual(second.status_code, 200)
        # Verify in-memory model_cache prevented reloading weights on the second request
        self.assertEqual(mock_tok.call_count, 1)
        self.assertEqual(mock_cls.call_count, 1)
        fake_model.eval.assert_called_once()

    def test_generate_with_huggingface_causal_lm_slices_prompt_tokens(self):
        fake_tokenizer = MagicMock()
        fake_tokenizer.pad_token_id = None
        fake_tokenizer.eos_token_id = 50256
        # Input prompt has 3 tokens: [101, 102, 103]
        fake_tokenizer.return_value = FakeInputs({"input_ids": torch.tensor([[101, 102, 103]])})
        fake_tokenizer.decode.return_value = "Generated continuation"

        fake_model = MagicMock()
        fake_model.to.return_value = fake_model
        # CausalLM returns prompt tokens [101, 102, 103] + new tokens [201, 202]
        fake_model.generate.return_value = torch.tensor([[101, 102, 103, 201, 202]])

        with (
            patch.object(ai_service.AutoTokenizer, "from_pretrained", return_value=fake_tokenizer),
            patch.object(ai_service.AutoModelForCausalLM, "from_pretrained", return_value=fake_model),
        ):
            response = self.client.post(
                "/generate",
                json={"message": "Hello world", "backend": "huggingface", "model": "gpt2"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["response"], "Generated continuation")
        decoded_tensor = fake_tokenizer.decode.call_args.args[0]
        self.assertEqual(decoded_tensor.tolist(), [201, 202])

    def test_generate_with_ollama_success_and_error_handling(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "Ollama local response"}
        mock_resp.raise_for_status.return_value = None

        with patch.object(ai_service.requests, "post", return_value=mock_resp) as mock_post:
            ok_response = self.client.post(
                "/generate",
                json={"message": "Write Python", "backend": "ollama", "model": "mistral:latest"},
            )
            self.assertEqual(ok_response.status_code, 200)
            self.assertEqual(ok_response.get_json()["response"], "Ollama local response")
            mock_post.assert_called_once()

        with patch.object(
            ai_service.requests,
            "post",
            side_effect=requests.ConnectionError("Connection refused"),
        ):
            err_response = self.client.post(
                "/generate",
                json={"message": "Write Python", "backend": "ollama"},
            )
            self.assertEqual(err_response.status_code, 502)
            self.assertIn("Ollama request failed", err_response.get_json()["error"])

    def test_wake_send_command_to_ai_posts_expected_payload(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "Voice assistant reply"}
        mock_resp.raise_for_status.return_value = None

        with patch.object(wake.requests, "post", return_value=mock_resp) as mock_post:
            reply = wake.send_command_to_ai(
                "What time is it?",
                api_url="http://127.0.0.1:5001/generate",
                backend="huggingface",
                model="flan-t5",
            )

        self.assertEqual(reply, "Voice assistant reply")
        mock_post.assert_called_once_with(
            "http://127.0.0.1:5001/generate",
            json={"message": "What time is it?", "backend": "huggingface", "model": "flan-t5"},
            timeout=60,
        )


if __name__ == "__main__":
    unittest.main()
