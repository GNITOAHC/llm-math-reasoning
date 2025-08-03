import os
import sys

def rename_dataset_files(directory_path):
    """
    Renames paired .desc.txt and .ans.txt files in a directory
    from a format like 'basename.desc.txt' to 'q_i_desc.txt'.
    """
    print(f"指定的資料夾路徑: {directory_path}")

    # 檢查路徑是否存在
    if not os.path.isdir(directory_path):
        print(f"錯誤：找不到資料夾 '{directory_path}'。請檢查路徑是否正確。")
        return

    try:
        # 獲取資料夾中的所有檔案
        all_files = os.listdir(directory_path)
    except OSError as e:
        print(f"錯誤：無法讀取資料夾內容。 {e}")
        return
        
    # 1. 找出所有 .desc.txt 檔案，並進行排序以確保命名順序一致
    desc_files = sorted([f for f in all_files if f.endswith('.desc.txt')])

    if not desc_files:
        print("在資料夾中沒有找到任何符合 '.desc.txt' 格式的檔案。")
        return

    print(f"找到了 {len(desc_files)} 個 .desc.txt 檔案，準備開始重新命名...")
    
    # 2. 初始化計數器
    counter = 1
    renamed_count = 0

    # 3. 遍歷找到的 desc 檔案並重新命名
    for desc_filename in desc_files:
        # 從 'DSJC250.1.desc.txt' 推斷出 basename 'DSJC250.1'
        basename = desc_filename.removesuffix('.desc.txt')
        
        # 建立對應的 ans 檔案名稱
        ans_filename = f"{basename}.ans.txt"

        # 建立原始檔案的完整路徑
        original_desc_path = os.path.join(directory_path, desc_filename)
        original_ans_path = os.path.join(directory_path, ans_filename)

        # 安全檢查：確認成對的 ans 檔案確實存在
        if not os.path.exists(original_ans_path):
            print(f"警告：找到了 {desc_filename} 但找不到對應的 {ans_filename}。跳過此對檔案。")
            continue

        # 建立新的檔案名稱
        new_desc_filename = f"q_{counter}_desc.txt"
        new_ans_filename = f"q_{counter}_ans.txt"

        # 建立新檔案的完整路徑
        new_desc_path = os.path.join(directory_path, new_desc_filename)
        new_ans_path = os.path.join(directory_path, new_ans_filename)

        try:
            # 執行重新命名
            os.rename(original_desc_path, new_desc_path)
            print(f"  {desc_filename}  ->  {new_desc_filename}")
            
            os.rename(original_ans_path, new_ans_path)
            print(f"  {ans_filename}  ->  {new_ans_filename}")
            
            renamed_count += 2
            counter += 1
        except OSError as e:
            print(f"錯誤：重新命名檔案時發生錯誤。 {e}", file=sys.stderr)


    print(f"\n重新命名完成！總共有 {renamed_count} 個檔案被成功更名。")

# --- 主程式執行區 ---
if __name__ == "__main__":
    # 請在此處設定您的資料夾路徑
    target_directory = "/Users/harry/Desktop/x/nlp-quantum/datasets/dataset_GCP/new_output"
    
    rename_dataset_files(target_directory)