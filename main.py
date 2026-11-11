import sys
from datetime import datetime
from database import init_db, upsert_shift, get_monthly_stats, get_shifts_by_month

def print_header() -> None:
    print("\n" + "=" * 50)
    print(" 📅 SHIFT TRACKER CLI v1.0")
    print("=" * 50 + "\n")

def get_valid_date() -> str:
    while True:
        date_str = input("Введите дату (ГГГГ-ММ-ДД): ").strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("❌ Неверный формат. Используйте ГГГГ-ММ-ДД.")

def get_valid_float(prompt: str) -> float:
    while True:
        user_input = input(prompt).strip().replace(',', '.')
        try:
            value = float(user_input)
            if value < 0:
                print("❌ Значение не может быть отрицательным.")
                continue
            return value
        except ValueError:
            print("❌ Неверный ввод. Введите число.")

def cmd_add_shift() -> None:
    print("\n--- Добавление или обновление смены ---")
    date = get_valid_date()
    hours = get_valid_float("Количество часов: ")
    rate = get_valid_float("Ставка в час (₽): ")
    note = input("Примечание (Enter, если нет): ").strip()

    if upsert_shift(date, hours, rate, note):
        total = round(hours * rate, 2)
        print(f"✅ Успешно! Смена за {date} сохранена. Заработок: {total} ₽")
    else:
        print("❌ Не удалось сохранить данные.")

def cmd_view_month() -> None:
    print("\n--- Статистика за месяц ---")
    try:
        current_year = datetime.now().year
        year_input = input(f"Год (по умолчанию {current_year}): ").strip()
        year = int(year_input) if year_input else current_year
        
        month_input = input("Месяц (1-12): ").strip()
        month = int(month_input)
        if not (1 <= month <= 12):
            raise ValueError
    except ValueError:
        print("❌ Неверный ввод года или месяца.")
        return

    stats = get_monthly_stats(year, month)
    shifts = get_shifts_by_month(year, month)

    print(f"\n📊 Итого за {month:02d}.{year}:")
    print(f"   Отработано часов: {stats['total_hours']:.1f}")
    print(f"   Заработано:       {stats['total_earnings']:,.2f} ₽")

    if not shifts:
        print("\nℹ️ Смен за этот месяц не найдено.")
        return

    print("\n📋 Детализация смен:")
    print(f"{'Дата':<12} | {'Часы':<6} | {'Ставка':<8} | {'Итого':<10} | {'Примечание'}")
    print("-" * 68)
    for s in shifts:
        note_display = (s['note'][:12] + "...") if len(s['note'] or "") > 15 else (s['note'] or "-")
        print(f"{s['date']:<12} | {s['hours']:<6.1f} | {s['rate']:<8.2f} | {s['total']:<10.2f} | {note_display}")

def main() -> None:
    init_db()
    while True:
        print_header()
        print("1. ➕ Добавить/обновить смену")
        print("2. 📊 Статистика и смены за месяц")
        print("3. 🚪 Выход")

        choice = input("\nВыберите действие (1-3): ").strip()

        if choice == "1":
            cmd_add_shift()
        elif choice == "2":
            cmd_view_month()
        elif choice == "3":
            print("\n👋 До встречи! Хороших заработков, босс!\n")
            sys.exit(0)
        else:
            print("❌ Неверный выбор. Введите число от 1 до 3.")

if __name__ == "__main__":
    main()
