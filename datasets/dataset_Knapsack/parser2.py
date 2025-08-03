import re
import os

def parse_knapsack_file(file_path, output_dir):
    """
    解析背包問題的資料檔案，並為每個問題實例生成描述檔和答案檔。

    Args:
        file_path (str): 輸入資料檔案的完整路徑。
        output_dir (str): 輸出檔案要存放的目錄。
    """
    try:
        # 使用 utf-8 編碼讀取檔案
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{file_path}'。請確認檔案路徑是否正確。")
        return
    except Exception as e:
        print(f"讀取檔案時發生錯誤：{e}")
        return

    # 使用 '-----\n\n' 作為分隔符來切分不同的問題實例
    problem_blocks = re.split(r'\n-----\s*\n', content.strip())

    # 過濾掉切分後可能產生的空區塊
    problem_blocks = [block for block in problem_blocks if block.strip()]
    
    if not problem_blocks:
        print("警告：在檔案中找不到任何有效的問題區塊。請檢查檔案格式和分隔符。")
        return

    # --- 新增：定義要加在檔案開頭的文字 ---
    problem_description = """Problem: 0/1 Knapsack Optimization from CSV
You are given a list of items in a CSV format. Each item has a value and a weight. Your task is to select a subset of these items to put into a knapsack such that:

The total weight should not be exceeded.

The total value is maximized.

You cannot take fractional items, and you cannot take the same item more than once.
"""

    # 逐一處理每個問題區塊
    for block in problem_blocks:
        lines = block.strip().split('\n')
        
        problem_name_line = lines[0]
        problem_id_match = re.search(r'_(\d+)$', problem_name_line)
        if not problem_id_match:
            print(f"警告：無法從 '{problem_name_line}' 中提取問題 ID，跳過此區塊。")
            continue
        problem_id = problem_id_match.group(1)

        try:
            c_line = next(line for line in lines if line.strip().startswith('c '))
            z_line = next(line for line in lines if line.strip().startswith('z '))
            c = int(c_line.split(' ')[1])
            z = int(z_line.split(' ')[1])
        except (StopIteration, IndexError, ValueError) as e:
            print(f"警告：解析問題 {problem_id} 的元數據 (c 或 z) 時出錯，跳過。錯誤：{e}")
            continue

        item_lines = [line for line in lines if ',' in line]
        items = []
        for line in item_lines:
            try:
                parts = line.split(',')
                if len(parts) == 4:
                    items.append({'value': int(parts[1]), 'weight': int(parts[2])})
                else:
                    print(f"警告：問題 {problem_id} 的物品資料格式不正確，已跳過此行：'{line}'")
            except (IndexError, ValueError) as e:
                print(f"警告：解析問題 {problem_id} 的物品資料時出錯，跳過此行 '{line}'。錯誤：{e}")
                continue

        # --- 生成 q{i}.desc.txt ---
        # 將輸出檔案路徑設定在指定的 output_dir 中
        desc_filename = os.path.join(output_dir, f'q{problem_id}.desc.txt')
        with open(desc_filename, 'w', encoding='utf-8') as f_desc:
            # --- 修改：先寫入問題描述 ---
            f_desc.write(problem_description)
            f_desc.write("\n---\n\n") # 加入分隔線
            f_desc.write(f'total weight: {c}\n')
            f_desc.write('value,weight\n')
            for item in items:
                f_desc.write(f"{item['value']},{item['weight']}\n")
            f_desc.write("\n---\n\n") # 加入分隔線
            f_desc.write(f'Please maximize the value and give me the answer.\n')

        # --- 生成 q{i}.ans.txt ---
        # 將輸出檔案路徑設定在指定的 output_dir 中
        ans_filename = os.path.join(output_dir, f'q{problem_id}.ans.txt')
        with open(ans_filename, 'w', encoding='utf-8') as f_ans:
            f_ans.write(f'{z}\n')
                
    print(f"成功處理了 {len(problem_blocks)} 個問題實例。")
    print(f"所有檔案均已成功生成於: {output_dir}")


# --- 主程式執行區 ---
if __name__ == "__main__":
    # 取得此腳本檔案所在的目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # --- 新增：設定輸出資料夾 ---
    # 設定新資料夾的名稱
    output_folder_name = 'parsed_results'
    # 將腳本目錄和新資料夾名稱組合成完整的輸出路徑
    output_dir_path = os.path.join(script_dir, output_folder_name)
    
    # 建立資料夾，如果它不存在的話
    # exist_ok=True 確保如果資料夾已存在，程式不會報錯
    os.makedirs(output_dir_path, exist_ok=True)
    
    # 指定要解析的 CSV 檔案名稱 🌟 在 original_csv 裡面

    csv_filename = 'knapPI_1_100_1000.csv'
    
    # 將腳本目錄和檔案名稱組合成完整的檔案路徑
    file_to_parse = os.path.join(script_dir, csv_filename)
    
    # 呼叫主函數，並將新的輸出目錄路徑傳入
    parse_knapsack_file(file_to_parse, output_dir_path)
