# 5장. 로컬 LLM과 LiteLLM 통합하기

검증 환경: Ollama 0.34.0 (CPU: Intel N100 / GPU: RTX 3060 12GB), vLLM 0.31.0 (RTX 3090 24GB), LiteLLM 1.106.1

## 로컬 추론 서버 실행

```bash
# Ollama (CPU 또는 GPU) — 소형 모델
docker run -d --name ollama -p 11434:11434 -v ollama:/root/.ollama ollama/ollama:0.34.0
docker exec ollama ollama pull qwen3.5:2b

# vLLM (NVIDIA GPU 24GB) — Qwen3.5-9B BF16
docker run -d --name vllm --gpus all --ipc=host -p 8000:8000 \
  -v $HOME/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:v0.31.0 Qwen/Qwen3.5-9B \
  --served-model-name qwen3.5-9b --max-model-len 16384 --gpu-memory-utilization 0.90 --max-num-seqs 32 \
  --limit-mm-per-prompt '{"image":0,"video":0}' \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3
```

`.env`에 추가:

```bash
OLLAMA_API_BASE=http://host.docker.internal:11434   # Proxy 컨테이너에서 같은 서버의 Ollama
VLLM_API_BASE=http://<GPU-서버-주소>:8000/v1
```

Proxy 컨테이너는 `--add-host=host.docker.internal:host-gateway`를 붙여 실행합니다. SDK 예제(`local_call.py`)를 호스트에서 직접 돌릴 때는 `OLLAMA_API_BASE=http://localhost:11434`로 바꿉니다.

## 파일

| 파일 | 페이지 | 내용 |
|---|---|---|
| `local_call.py` | 05-2, 05-3 | SDK로 Ollama·vLLM 호출 |
| `config.yaml` | 05-4 | 로컬 2개 + 클라우드 2개 별칭 |
| `compare_local_cloud.py` | 05-4 | Gateway 경유 로컬·클라우드 비교 |
