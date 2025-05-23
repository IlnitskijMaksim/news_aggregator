import os
import uuid

def generate_config():
    # Визначаємо, куди писати config.py (на рівень вище поточної директорії)
    target_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
    os.makedirs(target_dir, exist_ok=True)
    student_path = os.path.join(target_dir, "student_id.txt")
    with open(student_path, encoding='utf-8') as f:
        student = f.read().strip()
        student_id = f"{student}_{uuid.uuid4().hex[:8]}"
        content = f'''STUDENT_ID = "{student_id}"
SOURCES = []
'''
    config_path = os.path.join(target_dir, "config.py")
    with open(config_path, 'w', encoding='utf-8') as cfg:
        cfg.write(content)