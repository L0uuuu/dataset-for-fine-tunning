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
multi_turn_pairs = []

for i, entry in enumerate(data):
    messages = entry.get('messages', [])
    turn_number = 0
    
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            if content:
                questions.append((i + 1, content))
                turn_number += 1
                multi_turn_pairs.append((i + 1, turn_number, 'user', content))
        elif msg.get('role') == 'assistant':
            content = msg.get('content', '')
            if content:
                multi_turn_pairs.append((i + 1, turn_number, 'assistant', content))

SEPARATOR = '-' * 80

# Text file — labeled Question/Answer with separator lines
with open(output_txt, 'w', encoding='utf-8') as f:
    for i, entry in enumerate(data):
        f.write(f"{'=' * 80}\n")
        f.write(f"CONVERSATION {i + 1}\n")
        f.write(f"{'=' * 80}\n\n")
        messages = entry.get('messages', [])
        for msg_idx, msg in enumerate(messages):
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'system':
                continue
            elif role == 'user':
                label = 'QUESTION'
            elif role == 'assistant':
                label = 'ANSWER'
            else:
                label = role.upper()
            f.write(f"[{label}]\n{content}\n\n")
            f.write(f"{SEPARATOR}\n\n")

# CSV file — includes all user/assistant pairs with turn numbers
with open(output_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['conversation_index', 'turn_number', 'role', 'content'])
    for conv_idx, turn, role, content in multi_turn_pairs:
        writer.writerow([conv_idx, turn, role, content])

print(f"Done. {len(questions)} user messages extracted.")
print(f"  Text: {output_txt}")
print(f"  CSV:  {output_csv} ({len(multi_turn_pairs)} total messages with roles)")
