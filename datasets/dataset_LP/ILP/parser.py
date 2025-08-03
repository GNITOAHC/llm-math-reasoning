import os
import re

# Input and output directories
input_file = "./nl4opt_expr_ans.txt"  # Replace with your actual file name
output_dir = "parsed_output"
os.makedirs(output_dir, exist_ok=True)

# Read the entire file content
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# Split by documents using the "======================" delimiter
documents = [
    doc.strip() for doc in content.split("======================") if doc.strip()
]

# Regex patterns
answer_pattern = re.compile(r"\[ Answer \]\s*(.*)", re.DOTALL)

for idx, doc in enumerate(documents, start=1):
    # Extract answer
    answer_match = answer_pattern.search(doc)
    answer_text = answer_match.group(1).strip() if answer_match else ""

    # Description is everything before [ Answer ]
    desc_text = doc.split("[ Answer ]")[0].strip()

    # Remove "[ Document x ]" from description
    desc_text = re.sub(r"\[ Document \d+ \]\s*", "", desc_text)

    # Write description to file
    desc_filename = os.path.join(output_dir, f"q{idx}.desc.txt")
    with open(desc_filename, "w", encoding="utf-8") as desc_file:
        desc_file.write(desc_text.strip())

    # Write answer to file
    ans_filename = os.path.join(output_dir, f"q{idx}.ans.txt")
    with open(ans_filename, "w", encoding="utf-8") as ans_file:
        ans_file.write(answer_text)

print(f"Parsing complete. Files saved in '{output_dir}' directory.")
