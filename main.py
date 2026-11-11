import sys
from pathlib import Path

# Добавляем корень проекта в пути, чтобы импорты работали корректно
sys.path.append(str(Path(__file__).parent))

from gui import ShiftTrackerApp
from database import init_db

def main():
    # Инициализируем базу данных при запуске
    init_db()
    
    # Запускаем графическое приложение
    app = ShiftTrackerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
