# 📌 README — Sakura Moyu VH (Vietnamese Translation Project)

> ## ⚠️ AI: ĐỌC FILE NÀY TRƯỚC KHI LÀM BẤT CỨ ĐIỀU GÌ
>
> File này chứa quy tắc bắt buộc của project. Vi phạm bất kỳ quy tắc nào đều làm hỏng toàn bộ tính nhất quán của bản dịch.

---

## Cấu Trúc Thư Mục

```
_trans/
├── README.md              ← FILE NÀY (đọc trước tiên)
├── analysis_report.md     ← Báo cáo tiến độ toàn project
├── script_excel/          ← 147 file xlsx (toàn bộ script game)
├── context/               ← Ngữ cảnh dịch thuật chi tiết
│   ├── translation_context.md  ← Index tổng hợp (đọc trước)
│   ├── characters.md           ← Database nhân vật + xưng hô
│   ├── glossary.md             ← Bảng thuật ngữ cố định
│   ├── arc_common.md           ← Ngữ cảnh Prologue + Common
│   ├── arc_kuro.md             ← Ngữ cảnh Arc Kuro
│   ├── arc_haru.md             ← Ngữ cảnh Arc Haru
│   ├── arc_chiwa.md            ← Ngữ cảnh Arc Chiwa
│   └── arc_hiori.md            ← Ngữ cảnh Arc Hiori
├── MCP/                   ← MCP tools server (12 tools)
│   ├── server.py               ← Server chính
│   └── requirements.txt
├── promts/                ← Prompt templates
│   └── test.md                 ← Prompt chuẩn (dùng để dịch)
├── scripts/               ← Python scripts tiện ích
│   ├── analyze_project.py      ← Phân tích + extract data
│   ├── generate_all.py         ← Tạo lại toàn bộ context files
│   └── analysis_cache/         ← Cache JSON (tự động tạo)
└── viethoa/               ← Output Việt hóa cuối cùng
```

---

## Cấu Trúc File xlsx

Mỗi file xlsx có các cột sau:

| Cột      | Nội dung                                 | Trạng thái                                |
| --------- | ----------------------------------------- | ------------------------------------------- |
| `raw`   | Script gốc (có tag VN)                  | Đọc tham khảo tag                        |
| `name`  | Tên nhân vật (JP)                      | Tra`characters.md`                        |
| `org`   | Văn bản Nhật gốc (sạch)              | Nguồn để dịch                           |
| `trans` | **Bản dịch người (bản thảo)** | Đúng nghĩa nhưng có thể dài/sai sót |
| `edit`  | **Bản dịch đã tinh chỉnh**     | CHUẨN NHẤT — dùng làm văn phong mẫu  |
| `merge` | Output cuối (merge edit vào raw)        | Không sửa trực tiếp                     |

> **Quy tắc ghi**: Khi AI dịch → ghi vào cột **`trans`**. Người dịch review → ghi vào **`edit`**.

---

## Quy Tắc Xưng Hô BẮT BUỘC

> Tra `context/characters.md` để xem đầy đủ. Bảng dưới là tóm tắt nhanh.

| Nhân vật                           | Xưng            | Với Taiga           | Với người khác                 |
| ------------------------------------ | ---------------- | -------------------- | ---------------------------------- |
| **大雅 (Taiga)** — POV chính | Tôi (nội tâm) | —                   | Tôi — Cậu/Em/Anh (tùy người) |
| **クロ (Kuro)**                | Em               | Em — Anh            | Em — Chị/Anh                     |
| **千和 (Chiwa)**               | Em               | Em — Anh/Tiền bối | Em — Anh Toa (Tomohito)           |
| **ハル (Haru)**                | Mình            | Mình — Taiga-kun   | Mình — tên/bạn                 |
| **智仁 (Tomohito)**            | Tớ              | Tớ — Cậu          | Tớ — Cậu                        |
| **あさひ (Asahi)**             | Chị             | Chị — Em           | Chị — Em                         |
| **十夜 (Tooya)**               | Em               | Em — Anh Taiga      | Em — Chị/Anh                     |
| **姫織 (Hiori)**               | Mình            | Mình — Taiga/cậu  | Mình — tên                      |
| **ナハト (Nacht)**             | Tôi/Ta          | Tôi/Ta — Ngươi   | Tùy tình huống                  |
| **ナナ (Nana)**                | Em               | Em — Anh            | Em — Chị (Haru)                  |

---

## Thuật Ngữ Cố Định

> Tra `context/glossary.md` để xem đầy đủ.

| JP        | VN                            | Ghi chú                                                                                                        |
| --------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 夜 (Yoru) | **Dạ**                 | nếu trong`“夜”` thì dịch là Dạ, còn nếu không có nháy kép thì dịch thành câu bình thường. |
| 夜の国    | **Dạ Quốc**           |                                                                                                                 |
| 悪夢      | **Ác mộng**           |                                                                                                                 |
| 迷い人    | **Người lạc lối**   |                                                                                                                 |
| 魔法少女  | **Ma pháp Thiếu nữ** | Viết hoa                                                                                                       |
| 魔法使い  | **Ma pháp sư**        |                                                                                                                 |
| 夢の寝床  | **Yume no Nedoko**      | Giữ nguyên tên JP                                                                                            |
| 三千の町  | **Thị trấn Sanzen**   | Giữ "Sanzen"                                                                                                   |
| 夜王 / 夜の王 / 夜の王さま | **Dạ Vương**         |                                                                                                                 |

---

## Quy Tắc Kỹ Thuật

1. **KHÔNG DỊCH tag VN**: `[p]`, `[r]`, `\n`, `@`, tên file `.jpg/.wav/.ogg`
2. **Giữ nguyên** `...` (ba chấm) — đây là pause quan trọng trong VN. KHÔNG dùng kết hợp dấu chấm ngay trước dấu ba chấm (như `. ...` hoặc `....`). Chỉ dùng duy nhất dấu ba chấm `...` theo đúng ngữ pháp Việt Nam.
3. **Giữ nguyên** `--` (câu bị ngắt) hoặc đổi thành `—`
4. **KHÔNG thêm** giải thích, chú thích cuối bản dịch
5. **KHÔNG gộp** các dòng — dịch từng dòng riêng biệt
6. Bản dịch phải **thuần Việt**, tự nhiên. Không bị "sặc mùi" dịch máy.
7. Bản dịch phải dịch chuẩn nghĩa không dịch chế dịch lung tung luyên thuyên.
8. **Văn phong tự nhiên, tránh "tu tiên"**: Không lạm dụng từ Hán-Việt hay từ cổ mang sắc thái kiếm hiệp/tu tiên (như "ngự", "ngự trị", "ngự ở đó") cho các hành động/trạng thái bình thường. Chỉ dùng văn phong bay bổng khi thật sự cần thiết (nội tâm sâu lắng, triết lý), bình thường cứ dịch giản dị, tự nhiên.
9. **Quy tắc chính tả i/y (Bộ Giáo dục 1984)**:
   - Thống nhất viết "i" cho âm cuối /i/ khi không thay đổi âm và nghĩa (ví dụ: `hi sinh`, `mĩ thuật`, `vật lí`, `kỉ niệm`, `thẩm mĩ`, `kì lạ`...).
   - Đứng sau âm đệm "u" thì viết "y" (ví dụ: `huy hiệu`, `quý báu`, `thủy chung`...).
   - Đứng một mình: từ Hán Việt viết "y" (`y khoa`, `ý nghĩa`, `y tá`...), từ thuần Việt viết "i" (`í ới`, `ì xèo`, `âm ỉ`...).
   - Ngoại lệ: Tên riêng (tên người, tên đất) viết theo cách truyền thống (`Lý Bôn`, `Lý Thường Kiệt`, `triều Lý`, `Phú Mỹ Hưng`...).

---

## Workflow Dịch Thuật (Dùng MCP)

```
1. get_file_list(arc="chiwa", status="partial")
   → Xem danh sách file cần dịch

2. get_context_for_file("sakumoyu-0094-chiwa_001.xlsx")
   → Lấy ngữ cảnh arc + nhân vật của file

3. get_few_shot_examples(character="千和", limit=8)
   → Lấy ví dụ văn phong tốt nhất của nhân vật

4. get_rows_to_translate("sakumoyu-0094-chiwa_001.xlsx", limit=25)
   → Lấy 25 dòng chưa dịch

5. [Dịch bằng prompt trong promts/test.md]

6. write_translations("sakumoyu-0094-chiwa_001.xlsx",
     [{"index": 5, "text": "Bản dịch VN"}, ...],
     column="trans")
   → Ghi kết quả

7. get_translation_stats(arc="chiwa")
   → Kiểm tra tiến độ
```

---

## Cài Đặt MCP Server

```bash
pip install -r MCP/requirements.txt
```

Cấu hình trong Claude Desktop / MCP client:

```json
{
  "mcpServers": {
    "sakura-moyu-vh": {
      "command": "python",
      "args": ["MCP/server.py"],
      "cwd": "d:\\sakura moyu\\_trans"
    }
  }
}
```

---

## Cập Nhật Context Files

Khi có thêm dữ liệu edit mới, chạy lại:

```bash
py -3 scripts/analyze_project.py
py -3 scripts/generate_all.py
```

---

*Project: Sakura Moyu Vietnamese Translation | Maintained by thanhbo50-star*
