# Test Results

Khung ghi ket qua cho rule-based prototype hien tai. Buoc nay moi test logic data -> retrieve -> rank -> answer draft, chua co LLM/UI/API that.

| Date | Tester | Test ID | Result | Evidence/Log | Issue found | Follow-up |
|---|---|---|---|---|---|---|
| 2026-06-04 | Codex | TC01 | Pass | `restaurant`, zone `Ben cang giao thoa`, confidence `high`, chon `Nha hang Deliland`. | Chua toi uu tie-break giua Deliland va Food Court cho nhu cau co tre nho + cho ngan. | Co the dieu chinh them weight `fast_service` va `low crowd`. |
| 2026-06-04 | Codex | TC03 | Pass | Fallback dung: khong co nha hang trong `100m` tu `River Safari`, answer noi ro khong khop hoan toan. | Goi y fallback van kha xa do mock data hien tai khong co restaurant gan khu nay. | Co the mo rong mock data hoac them fallback category gan hon. |
| 2026-06-04 | Codex | TC06 / TC11 | Pass | Khong chon `Quay kem River Safari` vi `closed`; fallback sang diem dang mo va giu `confidence=low`. | Lua chon thay the van xa va khong phai kem thuần tuy theo mock data. | Co the them mock data `ice_cream` dang mo de demo dep hon. |
| 2026-06-04 | Codex | TC09 | Pass | Constraint `nhanh`, `khong dong`, `co dieu hoa` day `Food Court` len top 1 voi confidence `high`. | Chua hien thi chi tiet constraint scoring tren UI vi chua co UI. | Debug trace da san sang de noi vao API/UI sau. |
| 2026-06-04 | Codex | TC10 | Pass | Parse duoc `has_children` va `exclude_tags=['spicy_options','cay']`; khong uu tien `Chingu`. | Chua parse sau hon cac preference am thuc phuc tap. | Co the bo sung parser `khong hai san`, `mon Nhat`, `do Han` sau. |
| 2026-06-04 | Codex | TC05 / TC12 | Pass | `medical`, zone `The gioi nuoc`, confidence `high`, chon `Diem so cuu The gioi nuoc`. | Chua co fast-track route tach rieng khoi ranking, nhung output da on dinh. | Neu can co the tach emergency flow thanh ham rieng. |
| 2026-06-04 | Codex | TC07 | Pass | `out_of_scope`, confidence `low`, khong fallback sang facility trong cong vien. | Chua co template rich response cho ngoai pham vi. | Co the them response variants o buoc API/UI. |

## Notes

- Co the chay smoke test bang `python codebase/tests/run_rule_tests.py`.
- Ket qua pass/fail chi phan anh rule-based prototype hien tai.
- Chua co LLM, UI, FastAPI that va chua co test tu dong bang pytest.
- Da bo sung `debug_trace`, `fallback_used`, `fallback_reason` de ho tro debug khi noi qua API/UI sau nay.
