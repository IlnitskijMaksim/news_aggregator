import importlib.util
from tools import gen_config

def test_config_generated(tmp_path, monkeypatch):
    # Перейти у tmp_path як робочу директорію
    monkeypatch.chdir(tmp_path)

    # Створити student_id.txt НА ОДИН РІВЕНЬ ВИЩЕ
    (tmp_path.parent / "student_id.txt").write_text("TestStudent", encoding="utf-8")

    # Виклик функції (зробить config.py також на рівень вище)
    gen_config.generate_config()

    # Завантажити config.py (також на рівень вище)
    import importlib.util
    config_path = tmp_path.parent / "config.py"
    spec = importlib.util.spec_from_file_location("config", str(config_path))
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)

    assert cfg.STUDENT_ID.startswith("TestStudent_")
    assert isinstance(cfg.SOURCES, list) and cfg.SOURCES == []