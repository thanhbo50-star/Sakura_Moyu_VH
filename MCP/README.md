# MCP Server — Sakura Moyu VH Translation Tools

## 12 Tools Có Sẵn

| Tool | Mô tả | Tiết kiệm token |
|------|--------|----------------|
| `get_file_list` | Danh sách file, filter theo arc/status | ⭐⭐⭐ |
| `get_rows_to_translate` | Lấy N dòng chưa dịch từ file (batch) | ⭐⭐⭐⭐⭐ |
| `get_translated_rows` | Xem dòng đã dịch để review | ⭐⭐⭐ |
| `write_translations` | Ghi kết quả dịch vào file | ⭐⭐⭐⭐⭐ |
| `get_context_for_file` | Ngữ cảnh arc + chars của file | ⭐⭐⭐⭐ |
| `get_few_shot_examples` | Ví dụ dịch tốt nhất theo nhân vật | ⭐⭐⭐⭐ |
| `get_translation_stats` | Tiến độ realtime | ⭐⭐⭐ |
| `search_translated` | Tìm kiếm trong bản dịch (kiểm tra nhất quán) | ⭐⭐⭐ |
| `get_character_voice` | Xưng hô + giọng điệu + ví dụ nhân vật | ⭐⭐⭐⭐ |
| `get_untranslated_count` | Đếm nhanh dòng chưa dịch | ⭐⭐ |
| `batch_get_rows` | Lấy rows từ nhiều file cùng lúc | ⭐⭐⭐⭐⭐ |
| `copy_trans_to_edit` | Copy trans → edit hàng loạt | ⭐⭐⭐ |

## Cài Đặt

```bash
pip install -r MCP/requirements.txt
```

## Cấu Hình Claude Desktop

Thêm vào `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sakura-moyu-vh": {
      "command": "python",
      "args": ["d:\\sakura moyu\\_trans\\MCP\\server.py"]
    }
  }
}
```

## Workflow Tối Ưu Token

Thay vì load cả file context → dùng `get_context_for_file` (chỉ trả arc liên quan).
Thay vì load cả file xlsx → dùng `get_rows_to_translate` với `limit=25`.
Dùng `batch_get_rows` để xem nhiều file trước khi chọn.
