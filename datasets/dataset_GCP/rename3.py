import os
import sys

def modify_ans_files_in_place(directory_path):
    """
    直接修改資料夾中所有 _ans.txt 檔案的內容，使其只剩下數字。
    """
    print(f"開始掃描資料夾: {directory_path}")
    print("警告：此操作將直接覆寫檔案內容，且無法復原。")

    # 檢查路徑是否存在
    if not os.path.isdir(directory_path):
        print(f"錯誤：找不到資料夾 '{directory_path}'。", file=sys.stderr)
        return

    # 1. 找出所有以 _ans.txt 結尾的檔案
    try:
        all_files = os.listdir(directory_path)
        ans_files = sorted([f for f in all_files if f.endswith('_ans.txt')])
    except OSError as e:
        print(f"錯誤：無法讀取資料夾內容。 {e}", file=sys.stderr)
        return

    if not ans_files:
        print("在資料夾中沒有找到任何符合 '_ans.txt' 格式的檔案。")
        return

    print(f"找到了 {len(ans_files)} 個答案檔案，準備就地修改...")
    
    modified_count = 0
    skipped_count = 0

    # 2. 遍歷所有答案檔案進行修改
    for filename in ans_files:
        file_path = os.path.join(directory_path, filename)
        new_content = None
        
        try:
            # --- 步驟一：讀取檔案並提取新內容 ---
            with open(file_path, 'r', encoding='utf-8') as f:
                original_line = f.readline()
            
            if 'Answer:' in original_line:
                parts = original_line.split('Answer:')
                number_str = parts[1].strip()
                
                # 驗證是否為數字
                try:
                    float(number_str)
                    new_content = number_str
                except ValueError:
                    print(f"  -> 跳過 {filename}：'{number_str}' 不是有效數字。")
                    skipped_count += 1
            else:
                print(f"  -> 跳過 {filename}：內容不含 'Answer:'。")
                skipped_count += 1
            
            # --- 步驟二：如果成功提取，則覆寫檔案 ---
            if new_content is not None:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  -> 已修改 {filename}，新內容為: {new_content}")
                modified_count += 1

        except Exception as e:
            print(f"處理檔案 {filename} 時發生錯誤: {e}", file=sys.stderr)
            skipped_count += 1

    print("\n--- 操作完成 ---")
    print(f"成功修改了 {modified_count} 個檔案。")
    if skipped_count > 0:
        print(f"跳過了 {skipped_count} 個檔案（因格式不符或錯誤）。")


# --- 主程式執行區 ---
if __name__ == "__main__":
    # 您之前重新命名檔案的資料夾路徑
    target_directory = "/Users/harry/Desktop/x/nlp-quantum/datasets/dataset_GCP/new_output"
    
    # 在執行前再次確認
    # answer = input(f"即將修改 '{target_directory}' 中的檔案，此操作無法復原。\n確定要繼續嗎？(y/n): ")
    # if answer.lower() == 'y':
    #     modify_ans_files_in_place(target_directory)
    # else:
    #     print("操作已取消。")
        
    # 如果您確定要執行且不想手動確認，請直接使用下面這行
    modify_ans_files_in_place(target_directory)