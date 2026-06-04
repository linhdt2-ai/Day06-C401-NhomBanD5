# Backend

Thu muc nay se chua backend prototype cho AI Assistant tai VinWonders.

Du kien backend se dieu phoi cac buoc: guardrail input, fast-track route, intent extraction, truy xuat mock data, ranking va response generation.

Hien tai backend da co ban rule-based toi thieu cho cac buoc:

- load va validate mock database JSON
- infer need type va current zone bang keyword
- retrieve candidate facilities theo category
- rank ket qua theo zone, khoang cach, status, crowd, wait va family/hot-weather hints
- tao `answer_draft` de test logic san pham
- bo sung `api.py` de expose local FastAPI endpoint `POST /api/chat` va `GET /health`

Chua co server, chua co API that, chua goi LLM va uu tien Python standard library.
