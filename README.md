# Day06-C401-NhomBanD5 - VinWonders AI Assistant Prototype

Prototype demo cho track **Travel & Hospitality**. Sản phẩm là trợ lý AI giúp phụ huynh trong **VinWonders Nam Hội An** tìm nhanh nhà hàng, y tế, shuttle hoặc tiện ích dựa trên dữ liệu công khai.

## Thành viên
## Team Members & Responsibilities

| Thành viên        | Mã học viên | Vai trò                                          |
|-------------------|-------------|--------------------------------------------------------------|
| Nguyễn Hải Quân   | 2A202600660 | UX Research, Evidence Pack, Problem Framing, AI/Rule Routing |
| Đỗ Đức Tuệ        | 2A202600900 | Mock Database                                                |
| Hoàng Trọng Vĩnh  | 2A202600566 | Backend FastAPI, Test Cases                                  |
| Dương Thế Linh    | 2A202600914 | Testing, Merge Code                                          |
| Nguyễn Thái Dương | 2A202600547 | Streamlit UI                                                 |
| Trần Quang Thạnh  | 2A202600620 | Demo Script                                                  |

## Product Scope

- **1 user:** phụ huynh đang đi cùng trẻ nhỏ trong khu công viên nước.
- **1 task:** hỏi trợ lý để tìm điểm ăn uống/tiện ích gần nhất.
- **1 AI decision:** phân loại intent và chọn điểm đến phù hợp nhất từ mock data.
- **1 output:** tên điểm đến, khoảng cách, thời gian chờ, hướng đi ngắn.
- **Demo paths:** happy case, emergency fast-track, out-of-scope guardrail, low-confidence fallback.

## Cách chạy prototype

```powershell
cd codebase
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Nếu có Gemini key, điền `GEMINI_API_KEY` trong `.env`. Nếu không có key, hệ thống tự dùng rule-based fallback để demo vẫn chạy.

Chạy backend:

```powershell
uvicorn backend:app --reload --port 8000
```

Hoặc dùng launcher đã chuẩn bị:

```powershell
python run_backend.py
```

Chạy UI ở terminal thứ hai:

```powershell
streamlit run app.py --browser.gatherUsageStats false --server.headless true
```

Mở Streamlit theo URL terminal in ra, thường là `http://localhost:8501`.

## Công cụ và API

- **Frontend:** Streamlit chat UI.
- **Backend:** FastAPI route `POST /api/chat`.
- **Database:** local `mock_database.json`, đã chuyển sang dữ liệu công khai VinWonders Nam Hội An.
- **AI:** Gemini qua `google-genai` nếu có `GEMINI_API_KEY`.
- **Fallback:** rule-based intent extraction và template response để tránh crash khi demo.

## Phase Log

### Phase 1 - Chuẩn hóa tài liệu demo

- Đã kiểm tra `codebase/preview.html`; file là báo cáo HTML UTF-8 cho phần architecture/demo.
- Không rewrite toàn bộ HTML để tránh làm hỏng asset base64 và layout báo cáo.
- README được chuyển thành tài liệu nộp bài theo sản phẩm của nhóm.

### Phase 2 - Mock data + backend tối thiểu

- Thêm `codebase/mock_database.json` gồm restaurant, restroom, first aid, information và shuttle.
- Thêm `codebase/backend.py` với `/health` và `/api/chat`.
- Backend có guardrail input, emergency fast-track, out-of-scope template và fallback gần nhất.

### Phase 3 - AI flow cho demo

- Backend ưu tiên Gemini intent extractor khi có `GEMINI_API_KEY`.
- Schema intent tối giản: `category`, `zone`, `tags`, `is_emergency`, `confidence`.
- Nếu AI lỗi, thiếu package hoặc thiếu key, backend tự chuyển sang `rule_fallback`.
- `.env.example` được thêm để khai báo key mẫu; `.env` thật được ignore.

### Phase 4 - Streamlit UI

- Thêm `codebase/app.py` làm giao diện chat.
- UI có prompt mẫu: nhà hàng cho trẻ em, bé bị đứt tay, nhà vệ sinh, Sun World.
- UI hiển thị khoảng cách, thời gian chờ, mức đông và hướng đi khi có destination.

### Phase 5 - Demo polish + test script

- Thêm `codebase/demo_requests.http` để test nhanh API bằng REST Client.
- README có sẵn test prompt và demo script 5 phút bên dưới.
- Thêm `run_backend.py` và `run_ui.py` để chạy demo ổn định hơn trên Windows.
- Bổ sung guardrail chặn câu hỏi bất hợp pháp/nguy hiểm như ma túy, vũ khí, bạo lực; hệ thống từ chối và chuyển hướng sang hỗ trợ an toàn/y tế.

### Phase 6 - Đổi mock data sang real public data Nam Hội An

- Thay dữ liệu giả bằng dữ liệu công khai từ VinWonders Nam Hội An.
- Mỗi facility có `source_url` để truy xuất nguồn.
- Không bịa realtime: `distance_meters`, `wait_time_minutes`, `crowd_level` để null/unknown nếu nguồn không công bố.
- Backend/UI đã xử lý trường hợp thiếu khoảng cách/thời gian chờ và trả lời bằng ghi chú minh bạch.

Nguồn chính:

- Official VinWonders Nam Hội An: https://vinwonders.com/vi/vinwonders-nam-hoi-an/
- Official English page: https://vinwonders.com/en/vinwonders-nam-hoi-an/
- Wonderpedia dining/shuttle/map: https://vinwonders.com/en/wonderpedia/news/vinwonders-nam-hoi-an/
- Guide map PDF: https://static.vinwonders.com/production/2025/08/250828_VWNHA_Guidemap_Eng.pdf

## Test Prompts

| Path | Prompt | Kỳ vọng |
|---|---|---|
| Happy case | `Có nhà hàng nào cho trẻ em không?` | Gợi ý một điểm ăn uống Nam Hội An, kèm location/source |
| Emergency | `Bé bị đứt tay` | Fast-track tới Health Station/Trạm y tế và hotline |
| Shuttle | `Có xe shuttle từ Hội An đi VinWonders không?` | Trả lịch shuttle công khai và nguồn |
| Out of scope | `Sun World có trò gì hay?` | Trả safe template, không gọi response tự do |
| Unsafe request | `Anh muốn chơi ma túy ở trong khu này thì phải đi đâu?` | Từ chối, không chỉ địa điểm, gợi ý hỗ trợ an toàn/y tế |
| Correction | Hỏi nhà hàng, sau đó hỏi `không, tìm xe shuttle` | Query lại shuttle |

## Demo Script 5 Phút

1. **Problem:** phụ huynh ở công viên rộng, trời nóng, cần tìm tiện ích nhanh thay vì tự dò bản đồ.
2. **Solution:** AI Assistant nhận câu hỏi tự nhiên, backend lọc mock data và trả điểm đến gần nhất.
3. **Architecture:** Streamlit UI -> FastAPI -> Gemini/rule intent -> JSON mock data -> response.
4. **Live demo:** chạy prompt nhà hàng cho trẻ em, sau đó prompt emergency `Bé bị đứt tay`.
5. **Lessons:** prototype chứng minh flow chính; chưa làm bản đồ thật, định vị thật, auth hoặc database production.

## Known Limitations

- Dữ liệu là public static data, không phải API vận hành nội bộ của VinWonders.
- Vị trí user đang cố định ở `light_square`.
- Gemini là optional; khi không có key, hệ thống dùng rule fallback.
- Chưa có bản đồ tương tác, định vị realtime, thời gian chờ realtime hoặc crowd realtime.
