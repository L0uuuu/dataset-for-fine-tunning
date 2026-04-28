"""import fitz  # PyMuPDF

def extract_text(pdf_path, output_path="output.txt"):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Text saved to {output_path}")

if __name__ == "__main__":
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "input.pdf"
    out = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    extract_text(pdf, out)"""

import json
import os
import glob

base = r'c:\Users\louai\OneDrive\Bureau\stage\data for fine tunning\constructed data'
output_file = os.path.join(base, 'all_messages.json')

all_messages = []

for filepath in glob.glob(os.path.join(base, '*.json')):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)

    # Handle both top-level object and top-level array
    if isinstance(data, list):
        examples = data
    else:
        examples = data.get('examples', [])

    for example in examples:
        if not isinstance(example, dict):
            continue
        messages = example.get('messages')
        if messages:
            all_messages.append({"messages": messages})

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_messages, f, ensure_ascii=False, indent=2)

print(f"Done. {len(all_messages)} conversations written to {output_file}")
