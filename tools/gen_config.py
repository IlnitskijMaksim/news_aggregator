import os
import uuid

def generate_config():
    # Додаємо створення директорії, якщо вона не існує
    os.makedirs('../backend', exist_ok=True)
    with open('../student_id.txt', encoding='utf-8') as f:
        student = f.read().strip()
        student_id = f"{student}_{uuid.uuid4().hex[:8]}"
        content = f'''STUDENT_ID = "{student_id}"
SOURCES    = []
'''
    with open('../backend/config.py', 'w', encoding='utf-8') as cfg:
        cfg.write(content)