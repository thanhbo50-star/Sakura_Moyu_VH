import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('sakumoyu-0112-chiwa_019.xlsx')

# Fix column name if it was altered
col_mapping = {}
for col in df.columns:
    if 'trans' in col and col != 'trans':
        col_mapping[col] = 'trans'
    if 'edit' in col and col != 'edit':
        col_mapping[col] = 'edit'
    if 'raw' in col and col != 'raw':
        col_mapping[col] = 'raw'
    if 'mtl' in col and col != 'mtl':
        col_mapping[col] = 'mtl'
    if 'org' in col and col != 'org':
        col_mapping[col] = 'org'
    if 'name' in col and col != 'name':
        col_mapping[col] = 'name'

if col_mapping:
    print(f"Renaming columns: {col_mapping}")
    df.rename(columns=col_mapping, inplace=True)

# Delete any extra columns
if 'trans_x000d_' in df.columns:
    df.drop(columns=['trans_x000d_'], inplace=True)

# Now define Natch's manual replacements
replacements = {
    55: "Ta sẽ hạn chế can dự vào cô bé hết mức có thể. Cậu thừa biết thì đừng có hỏi. Nhìn đi, ta xấu xí thế này cơ mà. Đáng sợ lắm. Là \"quái vật\" đấy.",
    56: "Kẻ như ta lại gần thì chỉ rước thêm vẻ hoảng sợ vô cớ của con bé thôi, còn lỡ nó mà khóc nữa thì mệt lắm. Dây dưa với bọn nhóc này đúng là phiền phức.",
    57: "Nên cậu cứ lo liệu hết đi, tự ôm cái trách nhiệm đó. Ta sẽ không nhúng tay vào đâu. Rõ chưa?",
    234: "Hừ. Ta đã bảo rồi mà.",
    348: "...Ta sẽ thử làm bánh kem. Sẽ cố hoàn thành nó trước khi hai người về. Sinh nhật thì phải có bánh ngọt chứ nhỉ?",
    350: "...Ta âm thầm tập luyện suốt đấy. Lần này chắc chắn sẽ làm tốt thôi. Ta cũng sẽ trang trí lại phòng. Con bé nhất định sẽ vui đúng không?"
}

changes = 0
for idx, new_trans in replacements.items():
    if idx in df.index:
        old_trans = str(df.at[idx, 'trans'])
        if old_trans != new_trans:
            print(f"Row {idx}:\nOld: {old_trans}\nNew: {new_trans}\n")
            df.at[idx, 'trans'] = new_trans
            changes += 1

# If there was a column rename or logic update
if changes > 0 or col_mapping:
    df.to_excel('sakumoyu-0112-chiwa_019.xlsx', index=False)
    print(f"Saved file with {changes} translation changes and fixed column names.")
else:
    print("No changes needed.")
