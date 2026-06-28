"""
Generate all context files, analysis report, and update prompt.
Run after analyze_project.py
"""
import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CACHE = r'd:\sakura moyu\_trans\scripts\analysis_cache'
BASE  = r'd:\sakura moyu\_trans'

with open(os.path.join(CACHE, 'arc_stats.json'), encoding='utf-8') as f:
    arc_stats = json.load(f)
with open(os.path.join(CACHE, 'char_examples.json'), encoding='utf-8') as f:
    char_examples = json.load(f)
with open(os.path.join(CACHE, 'file_stats.json'), encoding='utf-8') as f:
    file_stats = json.load(f)

# ─────────────────────────────────────────────
# 1. analysis_report.md
# ─────────────────────────────────────────────
def make_report():
    total_rows  = sum(s['rows'] for s in arc_stats.values())
    total_trans = sum(s['trans'] for s in arc_stats.values())
    total_edit  = sum(s['edit'] for s in arc_stats.values())
    total_files = sum(s['files'] for s in arc_stats.values())

    arc_display = {
        'prologue':     '📖 Prologue',
        'common':       '🏫 Common',
        'kuro':         '🐱 Arc Kuro',
        'haru':         '🌸 Arc Haru',
        'chiwa':        '🍡 Arc Chiwa',
        'hiori':        '🌙 Arc Hiori',
        'kuro_harem':   '💕 Harem Kuro',
        'haru_harem':   '💕 Harem Haru',
        'chiwa_harem':  '💕 Harem Chiwa',
        'hiori_harem':  '💕 Harem Hiori',
    }

    lines = [
        '# 📊 Sakura Moyu VH — Báo Cáo Phân Tích Project',
        '',
        '> **Auto-generated** từ script phân tích. Cập nhật bằng cách chạy lại `scripts/analyze_project.py` + `scripts/generate_all.py`',
        '',
        '## Tổng Quan',
        '',
        f'| Mục | Số lượng |',
        f'|-----|----------|',
        f'| Tổng số file | **{total_files}** |',
        f'| Tổng số dòng | **{total_rows:,}** |',
        f'| Dòng có bản dịch (`trans`) | **{total_trans:,}** ({round(total_trans/total_rows*100,1)}%) |',
        f'| Dòng đã tinh chỉnh (`edit`) | **{total_edit:,}** ({round(total_edit/total_rows*100,1)}%) |',
        f'| Dòng chưa dịch | **{total_rows-total_trans:,}** ({round((total_rows-total_trans)/total_rows*100,1)}%) |',
        '',
        '## Tiến Độ Theo Arc',
        '',
        '| Arc | Files | Dòng | Trans | Edit | Trạng thái |',
        '|-----|-------|------|-------|------|-----------|',
    ]

    arc_order = ['prologue', 'common', 'kuro', 'haru', 'chiwa', 'hiori',
                 'kuro_harem', 'haru_harem', 'chiwa_harem', 'hiori_harem']
    for arc in arc_order:
        if arc not in arc_stats:
            continue
        s = arc_stats[arc]
        pct_t = round(s['trans']/s['rows']*100, 1) if s['rows'] > 0 else 0
        pct_e = round(s['edit']/s['rows']*100, 1) if s['rows'] > 0 else 0
        name = arc_display.get(arc, arc)

        if pct_t >= 95: status = '✅ Gần hoàn thành'
        elif pct_t >= 50: status = '🔄 Đang dịch'
        elif pct_t > 0: status = '🟡 Mới bắt đầu'
        else: status = '⬜ Chưa dịch'

        lines.append(f'| {name} | {s["files"]} | {s["rows"]:,} | {s["trans"]:,} ({pct_t}%) | {s["edit"]} ({pct_e}%) | {status} |')

    lines += [
        '',
        '## Chi Tiết Từng File',
        '',
        '| # | File | Arc | Dòng | Trans% | Edit% | Trạng thái |',
        '|---|------|-----|------|--------|-------|-----------|',
    ]
    for i, fs in enumerate(file_stats, 1):
        if fs['pct_trans'] >= 95: st = '✅'
        elif fs['pct_trans'] >= 50: st = '🔄'
        elif fs['pct_trans'] > 0: st = '🟡'
        else: st = '⬜'
        lines.append(
            f'| {i:03d} | `{fs["file"]}` | {fs["arc"]} | {fs["rows"]} | {fs["pct_trans"]}% | {fs["pct_edit"]}% | {st} |'
        )

    lines += [
        '',
        '## Nhân Vật & Dữ Liệu Ví Dụ',
        '',
        '| Nhân vật | Ví dụ có sẵn | Ví dụ đã edit |',
        '|----------|-------------|--------------|',
    ]
    for char, examples in sorted(char_examples.items()):
        changed = len([e for e in examples if e['changed']])
        display = '*(Narrator/Nội tâm)*' if char == '__narrator__' else char
        lines.append(f'| {display} | {len(examples)} | {changed} |')

    lines += [
        '',
        '---',
        '*Báo cáo được tạo tự động. Chạy lại script để cập nhật.*'
    ]
    return '\n'.join(lines)


with open(os.path.join(BASE, 'analysis_report.md'), 'w', encoding='utf-8') as f:
    f.write(make_report())
print("✅ analysis_report.md")

# ─────────────────────────────────────────────
# 2. context/characters.md
# ─────────────────────────────────────────────
CHAR_DATA = {
    'あさひ': {
        'vn': 'Asahi (Himukai Asahi)',
        'role': 'Chị gái tinh thần, "Ma pháp sư" của thị trấn Sanzen',
        'personality': 'Trưởng thành, bí ẩn, ấm áp, mang phong thái chị đại dẫn dắt. Thỉnh thoảng bĩu môi duyên dáng.',
        'to_taiga': 'Chị — Em',
        'to_others': 'Chị — Em (với trẻ nhỏ/người quen)',
        'voice': 'Nhẹ nhàng, ôn hòa, đôi khi có ẩn ý sâu xa. Hay dùng câu hỏi phản chiếu.',
        'notes': 'Gọi Taiga bằng tên. Quản lý "Yume no Nedoko" — trại mồ côi/ngôi nhà.',
    },
    'クロ': {
        'vn': 'Kuro',
        'role': 'Cô bé mèo (cat-girl), sống tại Yume no Nedoko cùng Taiga',
        'personality': 'Ngây thơ, ít nói, nhút nhát, cực kỳ đáng yêu. Yêu thương Taiga sâu sắc.',
        'to_taiga': 'Em — Anh (Taiga)',
        'to_others': 'Em — Chị/Anh (tùy người)',
        'voice': 'Câu ngắn, hay ngập ngừng (...), dùng từ đơn giản, đôi khi thiếu chủ ngữ.',
        'notes': 'Hay bám víu Taiga. Nụ cười dịu dàng. Không thích người lạ.',
    },
    '大雅': {
        'vn': 'Taiga (Tendo Taiga)',
        'role': 'Nhân vật chính (nam), 18 tuổi, từ trại mồ côi',
        'personality': 'Tốt bụng, trầm tư, hay trêu Chiwa, dịu dàng với Kuro, thân thiện với Tomohito.',
        'to_chiwa': 'Tôi — Em (hay trêu là "Chibi-wa")',
        'to_kuro': 'Anh — Em',
        'to_asahi': 'Em — Chị (Chị Asahi)',
        'to_friends': 'Tôi — Cậu/Tomohito',
        'inner': 'Tôi (độc thoại/nội tâm)',
        'voice': '- Nội tâm: Trầm tư, triết lý, hơi tự trào, đôi khi bi quan.\n  - Hội thoại: Tốt bụng, hay đùa nhẹ.',
        'notes': 'POV chính. Hay dùng "..." trước câu quan trọng.',
    },
    '千和': {
        'vn': 'Chiwa (Andou Chiwa)',
        'role': 'Hậu bối (kouhai) năm nhất, con chủ quán cà phê',
        'personality': 'Lễ phép, nghiêm túc, hay bị Taiga trêu nên hay dỗi (phồng má, bĩu môi).',
        'to_taiga': 'Em — Anh (Senpai/Tiền bối)',
        'to_tomohito': 'Em — Anh Toa',
        'voice': 'Lịch sự, rõ ràng. Khi dỗi: đanh hơn, câu ngắn. Khi tự độc thoại: thành thật, nhẹ nhàng.',
        'notes': 'Tên thật: Andou Chiwa. Taiga hay gọi "Chibi-wa" (nhỏ bé). Con gái quán cà phê gia đình.',
    },
    '智仁': {
        'vn': 'Tomohito (Iguchi Tomohito / "Toa")',
        'role': 'Bạn thân từ nhỏ của Taiga, cùng lớp',
        'personality': 'Vui vẻ, lạc quan, hài hước, hay đùa giỡn. Gọi bản thân là "Rock\'n\'roller".',
        'to_taiga': 'Tớ — Cậu (hoặc Ông — Tôi khi đùa)',
        'to_others': 'Tớ — Cậu',
        'voice': 'Năng động, hay dùng từ lóng, câu ngắn gọn, tự tin. Hay cười ha hả.',
        'notes': 'Nickname: Toa (từ Tomohito → Toa). Chiwa gọi là "Anh Toa".',
    },
    'ハル': {
        'vn': 'Haru (Hiiragi Haru)',
        'role': 'Cựu Ma pháp Thiếu nữ, bạn thời thơ ấu của Taiga',
        'personality': 'Vui vẻ, ấm áp, hay lo lắng cho người khác. Muốn được dùng ma pháp lại.',
        'to_taiga': 'Mình — Taiga-kun',
        'to_others': 'Mình — bạn/tên nhân vật',
        'voice': 'Nhẹ nhàng, ấm áp, đôi khi phiền não. Hay thêm "á", "nha", "nè" cuối câu.',
        'notes': 'Dùng "Taiga-kun" thay vì chỉ "Taiga". Hay lo lắng cho Taiga khi liều lĩnh.',
    },
    '姫織': {
        'vn': 'Hiori (Yorutsuki Hiori)',
        'role': 'Bạn học, con nhà đền Yorutsuki ở khu "Dạ"',
        'personality': 'Điềm tĩnh, bí ẩn, đôi khi buồn bã. Thích Taiga.',
        'to_taiga': 'Mình — Taiga / cậu',
        'voice': 'Nhẹ nhàng, chậm rãi, đôi khi gợi nhớ. Câu ngắn khi buồn.',
        'notes': 'Gọi Taiga bằng tên. Hay xuất hiện một mình.',
    },
    '十夜': {
        'vn': 'Tooya',
        'role': 'Em nhỏ sống tại Yume no Nedoko',
        'personality': 'Năng động, vui vẻ, hào hứng. Đôi khi xấc nhưng đáng yêu.',
        'to_taiga': 'Em — Anh Taiga',
        'to_asahi': 'Em — Chị',
        'voice': 'Háo hức, hay thêm dấu "!", câu năng động. Đôi khi "xấc láo" một cách hài hước.',
        'notes': 'Hay bị Taiga dùng làm "đồng hành đêm". Thích đồ ngọt.',
    },
    'ナハト': {
        'vn': 'Nacht',
        'role': '"Quái vật của Dạ", cha nuôi của Chiwa, người kể chuyện bí ẩn',
        'personality': 'Trầm buồn, cô độc, ẩn chứa quan tâm sâu sắc. Đôi khi lạnh lùng tàn nhẫn (đóng vai ác).',
        'inner': 'Tôi',
        'to_outsiders': 'Ta — Ngươi (khi ra oai)',
        'to_chiwa': 'Tôi — Em/Cậu (hoặc gọi tên/\"con bé\"/\"tên đó\")',
        'voice': 'Trọng lượng, chậm rãi. Câu văn vẻ khi nội tâm. Ngắn gọn khi hội thoại.',
        'notes': 'Tên có nghĩa là "Đêm" (tiếng Đức). Thường xuất hiện trong các cảnh "Dạ Quốc".',
    },
    'ナナ': {
        'vn': 'Nana',
        'role': '"Vị thần nhỏ bé của Dạ Quốc", quản lý nhà ga cuối cùng',
        'personality': 'Thông thái, hay đùa giỡn nhưng sâu sắc. Nhỏ nhắn nhưng uy quyền.',
        'to_taiga': 'Em — Anh',
        'to_haru': 'Em — Chị (Haru)',
        'voice': 'Vui tươi nhưng có chiều sâu. Câu hay có ẩn dụ về "thời gian" và "số phận".',
        'notes': 'Sống tại "Nhà ga cuối cùng của thời gian". Hay bán/mua điều ước.',
    },
    'あず咲': {
        'vn': 'Azusa',
        'role': 'Chị gái/người quen của nhóm',
        'personality': 'Thân thiện, hay cười.',
        'notes': 'Xuất hiện ít. Chi tiết cần bổ sung khi có thêm dữ liệu edit.',
    },
    '？？？': {
        'vn': '??? (Nhân vật bí ẩn)',
        'role': 'Chưa rõ danh tính, thường xuất hiện trong flashback hoặc cảnh bí ẩn',
        'voice': 'Thường nói về "giấc mơ", "câu chuyện", "số phận". Giọng xa xăm, bí ẩn.',
        'notes': 'Có thể là nhiều nhân vật khác nhau tùy arc.',
    },
}

def make_characters_md():
    lines = [
        '# 👥 Database Nhân Vật — Sakura Moyu VH',
        '',
        '> **QUAN TRỌNG**: Bảng xưng hô dưới đây là BẮT BUỘC. Không được tự ý thay đổi.',
        '> Khi không chắc, ưu tiên theo ví dụ trong cột `edit` của file xlsx.',
        '',
        '---',
        '',
    ]

    for char_jp, data in CHAR_DATA.items():
        vn_name = data.get('vn', char_jp)
        lines.append(f'## {char_jp} — {vn_name}')
        lines.append('')
        lines.append(f'**Vai trò**: {data.get("role", "N/A")}  ')
        lines.append(f'**Tính cách**: {data.get("personality", "N/A")}  ')
        lines.append('')

        lines.append('**Xưng hô:**')
        for k, v in data.items():
            if k.startswith('to_') or k in ('inner',):
                label = k.replace('to_', 'Với ').replace('_', ' ').title()
                if k == 'inner': label = 'Nội tâm/độc thoại'
                lines.append(f'- {label}: `{v}`')
        lines.append('')

        lines.append(f'**Giọng điệu**: {data.get("voice", "N/A")}  ')
        if 'notes' in data:
            lines.append(f'**Ghi chú**: {data["notes"]}  ')
        lines.append('')

        # Add real examples from edit column
        if char_jp in char_examples:
            ex_list = char_examples[char_jp]
            changed = [e for e in ex_list if e['changed']]
            show = changed[:5] if changed else ex_list[:3]
            if show:
                lines.append('**Ví dụ thực tế** (từ bản dịch đã tinh chỉnh):')
                lines.append('')
                for e in show:
                    lines.append(f'> 🇯🇵 `{e["org"][:100]}`  ')
                    lines.append(f'> ✏️ trans: *{e["trans"][:100]}*  ')
                    lines.append(f'> ✅ edit: **{e["edit"][:100]}**  ')
                    lines.append('>')
        lines.append('---')
        lines.append('')

    return '\n'.join(lines)

os.makedirs(os.path.join(BASE, 'context'), exist_ok=True)
with open(os.path.join(BASE, 'context', 'characters.md'), 'w', encoding='utf-8') as f:
    f.write(make_characters_md())
print("✅ context/characters.md")

# ─────────────────────────────────────────────
# 3. context/glossary.md
# ─────────────────────────────────────────────
GLOSSARY = [
    ('夜 / Yoru / Dạ', 'Dạ', 'Hiện tượng đêm huyền bí trong game. LUÔN dịch là "Dạ" (viết hoa).'),
    ('夜の国 / Yoru no Kuni', 'Dạ Quốc', 'Thế giới bóng đêm nơi "Dạ" tồn tại.'),
    ('悪夢 / Akumu', 'Ác mộng', 'Sinh vật/hiện tượng xấu trong Dạ Quốc. Khi nói đến loài quái: "Ác mộng".'),
    ('迷い人 / Mayoibito', 'Người lạc lối', 'Người bị mắc kẹt trong Dạ Quốc. KHÔNG dịch là "kẻ lạc đường".'),
    ('魔法少女 / Mahou Shoujo', 'Ma pháp Thiếu nữ', 'Viết hoa cả hai từ. Số ít: "Ma pháp Thiếu nữ", số nhiều giống nhau.'),
    ('魔法使い / Mahou Tsukai', 'Ma pháp sư', 'Asahi = "Ma pháp sư của thị trấn".'),
    ('夢の寝床 / Yume no Nedoko', 'Yume no Nedoko', 'GIỮ NGUYÊN tên Nhật. Có thể thêm chú thích "(trại mồ côi/ngôi nhà)" lần đầu nhắc đến.'),
    ('三千の町 / Sanzen no Machi', 'Thị trấn Sanzen', 'GIỮ "Sanzen". Không dịch là "thị trấn ba nghìn".'),
    ('鍵 / Kagi', 'chìa khóa', 'Vật phẩm ma pháp. Viết thường trong câu, trừ khi nhấn mạnh: "Chìa khóa".'),
    ('夜王 / Yoru-ou', 'Dạ Vương', 'Kẻ thù cuối cùng. Viết hoa.'),
    ('時の果ての駅 / Toki no Hate no Eki', 'ga cuối của thời gian / Nhà ga cuối cùng của thời gian', 'Nơi Nana quản lý.'),
    ('最後の魔法 / Saigo no Mahou', 'Ma pháp cuối cùng', 'Kỹ năng đặc biệt của Haru.'),
    ('人生の試練 / Jinsei no Shiren', 'Thử thách cuộc đời', 'Phrase quan trọng trong arc Haru.'),
    ('...（ellipsis）', '...', 'GIỮ NGUYÊN dấu ba chấm. Không dùng "..." thành ",". Khoảng lặng quan trọng.'),
    ('[p] [r] \\n @', '(giữ nguyên)', 'TÚT NHIÊN KHÔNG DỊCH các tag kỹ thuật này. Giữ nguyên vị trí.'),
    ('r / \r', '(giữ nguyên)', 'Tag xuống dòng trong script VN. KHÔNG xóa hay dịch.'),
]

def make_glossary_md():
    lines = [
        '# 📖 Bảng Thuật Ngữ Cố Định — Sakura Moyu VH',
        '',
        '> Đây là bảng thuật ngữ **BẮT BUỘC**. Dù ngữ cảnh như thế nào cũng phải tuân theo.',
        '> Khi gặp term không có trong bảng, tham khảo thêm từ `characters.md` và các file arc.',
        '',
        '## Thuật Ngữ Thế Giới Game',
        '',
        '| Thuật ngữ JP | Bản dịch VN | Ghi chú |',
        '|-------------|------------|---------|',
    ]
    for jp, vn, note in GLOSSARY:
        lines.append(f'| `{jp}` | **{vn}** | {note} |')

    lines += [
        '',
        '## Tên Nhân Vật (Cách Gọi)',
        '',
        '| Tên JP | Tên VN | Cách gọi thông dụng |',
        '|--------|--------|---------------------|',
        '| 大雅 (Tendo Taiga) | Taiga | "Taiga", "anh", "tôi" (POV) |',
        '| 千和 (Andou Chiwa) | Chiwa | "Chiwa", "Chibi-wa" (Taiga trêu) |',
        '| クロ (Kuro) | Kuro | "Kuro", "em", "cô bé" |',
        '| ハル (Hiiragi Haru) | Haru | "Haru", "Haru-chan" |',
        '| 姫織 (Yorutsuki Hiori) | Hiori | "Hiori", "Hiyo-chan" |',
        '| 智仁 (Iguchi Tomohito) | Tomohito / Toa | "Tomohito", "Toa" |',
        '| あさひ (Himukai Asahi) | Asahi | "chị Asahi", "Asahi-san" |',
        '| 十夜 (Tooya) | Tooya | "Tooya", "em" |',
        '| ナナ (Nana) | Nana | "Nana-chan", "vị thần nhỏ" |',
        '| ナハト (Nacht) | Nacht | "Nacht", "ta" (khi ra oai) |',
        '',
        '## Quy Tắc Kỹ Thuật Bắt Buộc',
        '',
        '1. **Tag VN KHÔNG ĐƯỢC DỊCH**: `[p]`, `[r]`, `\\n`, `@`, tên file ảnh/âm thanh',
        '2. **Dấu ba chấm `...`**: Giữ NGUYÊN. Đây là pause quan trọng, không thay bằng dấu phẩy hay gạch ngang.',
        '3. **Dấu gạch ngang kép `--`**: Thường dùng cho câu bị ngắt đột ngột. Giữ nguyên hoặc dùng `—`.',
        '4. **Chữ nghiêng `*text*`**: Nhấn mạnh tâm lý. Có thể dùng `*text*` hoặc để nguyên.',
        '5. **Dấu ngoặc kép `「」`**: Chuyển thành dấu ngoặc kép thẳng `"..."` trong tiếng Việt.',
        '6. **Dấu ngoặc 「』**: Câu trích dẫn đặc biệt — dùng `『...』` giữ nguyên.',
        '7. **Không thêm giải thích**: Output chỉ là bản dịch. Không thêm chú thích cuối bài.',
    ]
    return '\n'.join(lines)

with open(os.path.join(BASE, 'context', 'glossary.md'), 'w', encoding='utf-8') as f:
    f.write(make_glossary_md())
print("✅ context/glossary.md")

# ─────────────────────────────────────────────
# 4. Arc context files
# ─────────────────────────────────────────────
ARC_CONTEXTS = {
    'arc_common': {
        'title': '🏫 Arc Common — Ngữ Cảnh Dịch Thuật',
        'files': 'sakumoyu-0001 đến sakumoyu-0051 (+ 0052)',
        'summary': '''Arc Common bao gồm Prologue và phần chung (Common route) của game.

**Cốt truyện chính:**
- Taiga rời trại mồ côi "Yume no Nedoko" sau 10 năm, bắt đầu cuộc sống mới
- Kuro (cô bé mèo) là người bạn thân nhất, luôn ở bên Taiga
- Haru (cựu Ma pháp Thiếu nữ) quay trở lại và muốn dùng ma pháp lần cuối
- Mọi người cùng nhau đi trên "con tàu của Nana" qua Dạ Quốc, thu thập điều ước
- Tooya (em nhỏ) là người dẫn đường trong Dạ Quốc

**Tone của arc**: Ấm áp, slice-of-life, xen lẫn huyền bí nhẹ. Cảm giác gia đình và bạn bè.
**Nhân vật xuất hiện nhiều**: Taiga, Kuro, Asahi, Haru, Tooya, Tomohito, Chiwa, Hiori, Nana''',
        'chars': ['大雅', 'クロ', 'あさひ', 'ハル', '十夜', '智仁', '千和', '姫織', 'ナナ'],
    },
    'arc_kuro': {
        'title': '🐱 Arc Kuro — Ngữ Cảnh Dịch Thuật',
        'files': 'sakumoyu-0053 đến sakumoyu-0074',
        'summary': '''Arc Kuro tập trung vào Kuro và bí mật của cô bé.

**Cốt truyện chính:**
- Câu chuyện sâu hơn về nguồn gốc của Kuro và "Dạ Quốc"
- Mối quan hệ giữa Taiga và Kuro được khắc họa sâu sắc hơn
- Kuro phải đối mặt với số phận như một "sinh vật của Dạ"

**Tone của arc**: Cảm xúc, u buồn, lãng mạn nhẹ nhàng. Đôi khi bi kịch.
**Nhân vật chính**: Taiga (POV), Kuro, Nacht
**Lưu ý**: Kuro hay nói câu ngắn, ngập ngừng. Nacht thay đổi giữa "Tôi" và "Ta" tùy tình huống.''',
        'chars': ['大雅', 'クロ', 'ナハト'],
    },
    'arc_haru': {
        'title': '🌸 Arc Haru — Ngữ Cảnh Dịch Thuật',
        'files': 'sakumoyu-0075 đến sakumoyu-0093',
        'summary': '''Arc Haru tập trung vào Haru và ước mơ trở lại là Ma pháp Thiếu nữ.

**Cốt truyện chính:**
- Haru muốn dùng "Ma pháp cuối cùng" cho một lý do quan trọng
- Taiga phải giúp Haru thực hiện "Thử thách cuộc đời" của cô
- Quá khứ của Haru và thời kỳ chiến đấu với "Dạ Vương" được hé lộ

**Tone của arc**: Ấm áp, cảm xúc sâu lắng, đôi chút bi thương. Haru hay dùng "-nha", "-nè", "-á".
**Nhân vật chính**: Taiga (POV), Haru, Asahi, Nana
**Lưu ý**: Haru gọi Taiga là "Taiga-kun". Hay lo lắng cho Taiga.''',
        'chars': ['大雅', 'ハル', 'あさひ', 'ナナ'],
    },
    'arc_chiwa': {
        'title': '🍡 Arc Chiwa — Ngữ Cảnh Dịch Thuật',
        'files': 'sakumoyu-0094 đến sakumoyu-0117',
        'summary': '''Arc Chiwa tập trung vào Chiwa và tình cảm của cô dành cho Taiga.

**Cốt truyện chính:**
- Chiwa tự hỏi tại sao mình thích Taiga
- Chiwa bỏ học một ngày, Taiga lo lắng và tìm cô
- Cha của Chiwa và quán cà phê gia đình đóng vai trò quan trọng
- Mối quan hệ giữa Chiwa và Nacht (cha nuôi bí ẩn) được hé lộ

**Tone của arc**: Dịu dàng, lãng mạn trong sáng, đôi khi hài hước nhẹ. Chiwa hay dỗi.
**Nhân vật chính**: Taiga (POV), Chiwa, Kuro, Nacht
**Lưu ý**: Chiwa gọi Taiga là "anh/tiền bối". Khi dỗi hay nói ngắn gọn, đanh hơn.''',
        'chars': ['大雅', '千和', 'クロ', 'ナハト'],
    },
    'arc_hiori': {
        'title': '🌙 Arc Hiori — Ngữ Cảnh Dịch Thuật',
        'files': 'sakumoyu-0118 đến sakumoyu-0139',
        'summary': '''Arc Hiori tập trung vào Hiori và bí mật của đền Yorutsuki.

**Cốt truyện chính:**
- Hiori và gia đình đền Yorutsuki có mối liên hệ đặc biệt với "Dạ Quốc"
- Hiori thích Taiga nhưng hay giấu cảm xúc
- Bí ẩn về "Dạ" và thị trấn được hé lộ qua lăng kính của Hiori

**Tone của arc**: Bí ẩn, nhẹ nhàng, đôi chút huyền bí. Hiori hay buồn bã hoặc xa xăm.
**Nhân vật chính**: Taiga (POV), Hiori, Asahi
**Lưu ý**: Hiori gọi Taiga bằng tên trực tiếp. Hay xuất hiện một mình hoặc khóc một mình.''',
        'chars': ['大雅', '姫織', 'あさひ'],
    },
}

for fname, adata in ARC_CONTEXTS.items():
    relevant_chars = adata['chars']
    lines = [
        f'# {adata["title"]}',
        '',
        f'**Files**: {adata["files"]}',
        '',
        '## Tóm Tắt Cốt Truyện',
        '',
        adata['summary'],
        '',
        '---',
        '',
        '## Ví Dụ Dịch Thuật Thực Tế',
        '',
        '> Các ví dụ dưới đây được trích từ cột `edit` (bản đã tinh chỉnh) của các file trong arc.',
        '',
    ]

    # Pull examples for relevant characters
    found_any = False
    for char in relevant_chars:
        if char in char_examples:
            ex_list = char_examples[char]
            changed = [e for e in ex_list if e['changed']]
            show = changed[:4] if changed else ex_list[:2]
            if show:
                found_any = True
                lines.append(f'### {char}')
                lines.append('')
                for e in show:
                    lines.append(f'**Gốc (JP)**: `{e["org"][:120]}`  ')
                    lines.append(f'**Trans (thảo)**: {e["trans"][:120]}  ')
                    lines.append(f'**Edit (chuẩn)**: **{e["edit"][:120]}**  ')
                    lines.append('')

    # Narrator examples
    if '__narrator__' in char_examples:
        lines.append('### Nội tâm / Narrator (không có name)')
        lines.append('')
        for e in char_examples['__narrator__'][:4]:
            lines.append(f'**Gốc (JP)**: `{e["org"][:120]}`  ')
            lines.append(f'**Trans (thảo)**: {e["trans"][:120]}  ')
            lines.append(f'**Edit (chuẩn)**: **{e["edit"][:120]}**  ')
            lines.append('')

    if not found_any:
        lines.append('*(Chưa có dữ liệu edit cho arc này — cần bổ sung sau khi dịch xong)*')

    with open(os.path.join(BASE, 'context', f'{fname}.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"✅ context/{fname}.md")

# ─────────────────────────────────────────────
# 5. Update context/translation_context.md (master)
# ─────────────────────────────────────────────
master_lines = [
    '# Sakura Moyu VH — Master Translation Context',
    '',
    '> **ĐỌC FILE NÀY TRƯỚC KHI DỊCH BẤT KỲ CÁI GÌ.**',
    '> File này tổng hợp link đến tất cả context chi tiết.',
    '',
    '## Quick Reference',
    '',
    '| Cần gì | Đọc file nào |',
    '|--------|-------------|',
    '| Xưng hô nhân vật | [`context/characters.md`](characters.md) |',
    '| Thuật ngữ cố định | [`context/glossary.md`](glossary.md) |',
    '| Ngữ cảnh arc Common/Prologue | [`context/arc_common.md`](arc_common.md) |',
    '| Ngữ cảnh arc Kuro | [`context/arc_kuro.md`](arc_kuro.md) |',
    '| Ngữ cảnh arc Haru | [`context/arc_haru.md`](arc_haru.md) |',
    '| Ngữ cảnh arc Chiwa | [`context/arc_chiwa.md`](arc_chiwa.md) |',
    '| Ngữ cảnh arc Hiori | [`context/arc_hiori.md`](arc_hiori.md) |',
    '| Tiến độ project | [`analysis_report.md`](../analysis_report.md) |',
    '| Prompt chuẩn | [`promts/test.md`](../promts/test.md) |',
    '',
    '## Quy Tắc Nhanh (Tóm Tắt)',
    '',
    '1. **Cột ưu tiên**: `edit` > `trans` > `org`. Khi dịch mới → điền vào `trans`.',
    '2. **Xưng hô**: Tra `characters.md` trước. Không tự ý dùng "tôi/bạn" đồng nhất.',
    '3. **Tag kỹ thuật**: `[p]` `[r]` `\\n` `@` → KHÔNG DỊCH, giữ nguyên.',
    '4. **Dấu ...**: Giữ nguyên, không xóa hay thay bằng dấu phẩy.',
    '5. **Thuật ngữ**: "Dạ" (không phải "đêm"), "Yume no Nedoko" (không dịch), "Dạ Quốc".',
    '',
]

with open(os.path.join(BASE, 'context', 'translation_context.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(master_lines))
print("✅ context/translation_context.md (updated)")

print("\n🎉 All context files generated!")
