# Codebase

## Scaffold hien tai cho AI Assistant tai VinWonders

Thu muc `codebase/` hien duoc chuan bi lam noi build prototype "AI Assistant tai VinWonders" dua tren SPEC va prototype README cua nhom.

Trang thai hien tai chi la scaffold/cau truc thu muc. Chua trien khai code chay that o buoc nay.

Vai tro cac thu muc:

- `data/`: chua mock database dang JSON cho dia diem, tien ich va trang thai demo.
- `prompts/`: chua khung prompt cho Intent Extractor va Response Generator.
- `backend/`: chua file Python skeleton cho backend, data loader, retriever, ranking va AI service.
- `frontend/`: chua file skeleton cho giao dien chat prototype.
- `tests/`: chua test case va khung ghi ket qua test theo cac duong di trong SPEC.

Luu y: Hien da co rule-based prototype cho luong data -> constraint -> retrieve -> rank -> fallback -> debug trace -> answer draft de test mock data va logic san pham. Da bo sung local FastAPI endpoint va Streamlit demo UI. LLM neu duoc bat chi dung de viet lai cau tra loi cuoi cung, khong thay rule engine va khong tu quyet dinh dia diem.

## Current status

- Mock data: done
- Rule-based engine: done
- Constraint parser: done
- Ranking/fallback/debug trace: done
- FastAPI local endpoint: done
- Streamlit demo UI: done
- UI-to-API integration: fallback-supported
- LLM integration: fallback-supported
- Real map/GPS/realtime data: not yet

## Chay demo local

```bash
# Chay rule tests
python codebase/tests/run_rule_tests.py

# Chay FastAPI neu da co fastapi/uvicorn
python -m uvicorn codebase.backend.api:app --reload

# Chay Streamlit UI neu da co streamlit
python -m streamlit run codebase/frontend/app.py
```

Neu may chua co `fastapi`, `uvicorn` hoac `streamlit` thi can cai trong moi truong rieng o buoc setup sau. Buoc nay khong tu dong cai package.

## Cau hinh LLM

Chay khong LLM:

```powershell
$env:LLM_PROVIDER="none"
```

Hoac trong `.env`:

```text
LLM_PROVIDER=none
```

Chay co LLM Gemini:

```powershell
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="your_key_here"
$env:LLM_MODEL="your_model_here"
```

Chay voi Gemini bang `.env` o root project:

```text
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_real_key_here
OPENROUTER_API_KEY=
```

Chay co LLM OpenRouter:

```powershell
$env:LLM_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="your_key_here"
$env:LLM_MODEL="your_model_here"
```

Chay voi OpenRouter bang `.env` o root project:

```text
LLM_PROVIDER=openrouter
LLM_MODEL=your_openrouter_model_here
GEMINI_API_KEY=
OPENROUTER_API_KEY=your_real_key_here
```

Khong commit `.env` hoac API key that. Chi commit `.env.example`. Neu chua co key, de `LLM_PROVIDER=none`. Neu thieu key hoac LLM loi, he thong tu fallback ve `answer_draft`.

---

Đây là nơi nhóm nộp toàn bộ phần code của prototype. Mục tiêu là để giảng viên và các nhóm khác nhìn được sản phẩm chạy như thế nào, và mỗi thành viên đã đóng góp ra sao.

## Nhóm cần làm

- Đưa mã nguồn của prototype vào folder này. Nếu prototype được deploy hoặc host ở nơi khác, hãy để lại đường link kèm hướng dẫn truy cập.
- Trong file `README.md` của nhóm, ghi rõ ba điều: cách chạy prototype (các bước cài đặt và biến môi trường nếu cần), những công cụ và API đã dùng (model AI, framework, công cụ dựng giao diện…), và phần phân công ai làm gì.
- Mỗi thành viên nên có ít nhất một commit thực chất trong repo — đây là căn cứ để ghi nhận đóng góp của từng người.

## Lưu ý

Đừng commit những thông tin nhạy cảm như API key hay file `.env`. Nếu prototype cần các biến môi trường, hãy dùng một file `.env.example` để mô tả các biến đó thay vì để lộ giá trị thật.
