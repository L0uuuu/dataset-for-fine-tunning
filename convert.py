import json
import os
import csv

base = r'c:\Users\louai\OneDrive\Bureau\stage\data for fine tunning\constructed data'
input_file = os.path.join(base, 'all_messages.json')
output_txt = os.path.join(base, 'all_questions.txt')
output_csv = os.path.join(base, 'all_questions.csv')

with open(input_file, encoding='utf-8') as f:
    data = json.load(f)

questions = []
for i, entry in enumerate(data):
    for msg in entry.get('messages', []):
        if msg.get('role') == 'user':
            questions.append((i + 1, msg['content']))

SEPARATOR = '-' * 80

# Text file — labeled Question/Answer with separator lines
with open(output_txt, 'w', encoding='utf-8') as f:
    for i, entry in enumerate(data):
        f.write(f"{'=' * 80}\n")
        f.write(f"CONVERSATION {i + 1}\n")
        f.write(f"{'=' * 80}\n\n")
        for msg in entry.get('messages', []):
            role = msg.get('role')
            if role == 'system':
                continue
            elif role == 'user':
                label = 'QUESTION'
            elif role == 'assistant':
                label = 'ANSWER'
            else:
                label = role.upper()
            f.write(f"[{label}]\n{msg['content']}\n\n")
            f.write(f"{SEPARATOR}\n\n")

# CSV file
with open(output_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['conversation_index', 'question'])
    for idx, q in questions:
        writer.writerow([idx, q])

print(f"Done. {len(questions)} questions extracted.")
print(f"  Text: {output_txt}")
print(f"  CSV:  {output_csv}")
