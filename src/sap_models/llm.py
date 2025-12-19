from __future__ import annotations

try:
    from llama_cpp import Llama
except Exception:  # pragma: no cover
    Llama = None


class LocalLLM:
    def __init__(self, gguf_path: str, n_ctx: int = 4096):
        if Llama is None:
            raise RuntimeError("llama-cpp-python not installed. Install with: pip install sap[models]")
        self.llm = Llama(model_path=gguf_path, n_ctx=n_ctx, verbose=False)

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        out = self.llm(prompt, max_tokens=max_tokens, temperature=temperature, stop=["</OUTPUT>"])
        return out["choices"][0]["text"].strip()
