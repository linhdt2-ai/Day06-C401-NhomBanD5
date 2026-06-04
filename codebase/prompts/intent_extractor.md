# Intent Extractor Prompt

## Muc dich

Prompt nay du kien dung de chuyen cau hoi ngon ngu tu nhien cua nguoi dung thanh intent co cau truc cho prototype AI Assistant tai VinWonders.

## Input du kien

- `user_input`: cau hoi cua nguoi dung.
- `user_context`: ngu canh gia lap, vi du `current_zone`, `has_kids`.

## Output JSON du kien

```json
{
  "need_type": "restaurant | restroom | first_aid | stroller | info | out_of_scope | malicious",
  "current_zone": "water_park",
  "constraints": {
    "kid_friendly": true,
    "has_ac": true,
    "max_distance_meters": 800,
    "max_wait_time_minutes": 10
  },
  "urgency": "normal | urgent",
  "confidence": "high | medium | low",
  "need_clarification": false,
  "clarifying_question": null
}
```

## Truong intent chinh

- `need_type`: nhom nhu cau cua nguoi dung.
- `current_zone`: khu vuc hien tai trong cong vien, co the la gia lap.
- `constraints`: cac rang buoc nhu phu hop tre em, co dieu hoa, gan nhat, thoi gian cho thap.
- `urgency`: muc do khan cap, dung cho fast-track emergency.

## TODO

Hoan thien prompt chi tiet, guardrail va vi du input/output o buoc build prototype.
