# Run Demo

## Lenh chay

```bash
python codebase/tests/run_rule_tests.py
python -m uvicorn codebase.backend.api:app --reload
python -m streamlit run codebase/frontend/app.py
```

## URL local

- FastAPI health: `http://127.0.0.1:8000/health`
- FastAPI docs: `http://127.0.0.1:8000/docs`
- Streamlit UI: `http://localhost:8501`

## Ghi chu

- Streamlit UI uu tien goi `POST http://127.0.0.1:8000/api/chat`.
- Neu API chua chay hoac request loi, UI se fallback sang local `answer_with_rules()`.
- Co the chay khong LLM bang `LLM_PROVIDER=none`.
- Co the dat bien moi truong bang PowerShell hoac tao file `.env` o root project.
- PowerShell khong LLM:

```powershell
$env:LLM_PROVIDER="none"
```

- Hoac trong `.env`:

```text
LLM_PROVIDER=none
```

- PowerShell co LLM Gemini:

```powershell
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="your_key_here"
$env:LLM_MODEL="your_model_here"
```

- Chay voi Gemini bang `.env` o root project:

```text
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_real_key_here
OPENROUTER_API_KEY=
```

- PowerShell co LLM OpenRouter:

```powershell
$env:LLM_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="your_key_here"
$env:LLM_MODEL="your_model_here"
```

- Chay voi OpenRouter bang `.env` o root project:

```text
LLM_PROVIDER=openrouter
LLM_MODEL=your_openrouter_model_here
GEMINI_API_KEY=
OPENROUTER_API_KEY=your_real_key_here
```

- Khong commit API key that.
- Chi commit `.env.example`.
- Neu thieu key hoac LLM loi, he thong tu fallback ve `answer_draft`.
