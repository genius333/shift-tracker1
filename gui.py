import customtkinter as ctk
from tkinter import messagebox, END
from PIL import Image
from pathlib import Path
from datetime import datetime
from database import init_db, upsert_shift, get_monthly_stats, get_shifts_by_month

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ICON_PATH = Path(__file__).parent / "icon-2048.png"

class ShiftTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Shift Tracker - Учёт смен")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        if ICON_PATH.exists():
            self.iconphoto(True, ctk.CTkImage(light_image=Image.open(ICON_PATH), size=(32, 32)))
        
        self.setup_ui()
        self.load_current_month()
    
    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        header = ctk.CTkLabel(self, text="📅 Shift Tracker", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(input_frame, text="Дата:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(input_frame, placeholder_text="ГГГГ-ММ-ДД")
        self.date_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ctk.CTkLabel(input_frame, text="Часы:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.hours_entry = ctk.CTkEntry(input_frame, placeholder_text="8.0", width=100)
        self.hours_entry.grid(row=0, column=3, padx=10, pady=10)
        
        ctk.CTkLabel(input_frame, text="Ставка (₽):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.rate_entry = ctk.CTkEntry(input_frame, placeholder_text="500", width=100)
        self.rate_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(input_frame, text="Примечание:").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.note_entry = ctk.CTkEntry(input_frame, placeholder_text="Необязательно")
        self.note_entry.grid(row=1, column=3, padx=10, pady=10, sticky="ew")
        
        add_btn = ctk.CTkButton(input_frame, text="➕ Добавить смену", command=self.add_shift, fg_color="#00d4aa", hover_color="#00b894")
        add_btn.grid(row=2, column=0, columnspan=4, padx=10, pady=15, sticky="ew")
        
        stats_frame = ctk.CTkFrame(self)
        stats_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(1, weight=1)
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="📊 Статистика за месяц", font=ctk.CTkFont(size=18, weight="bold"))
        self.stats_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.shifts_textbox = ctk.CTkTextbox(stats_frame, font=ctk.CTkFont(family="Consolas", size=12))
        self.shifts_textbox.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        
        month_frame = ctk.CTkFrame(self)
        month_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(month_frame, text="Год:").grid(row=0, column=0, padx=10, pady=10)
        self.year_entry = ctk.CTkEntry(month_frame, width=80, placeholder_text=str(datetime.now().year))
        self.year_entry.grid(row=0, column=1, padx=10, pady=10)
        self.year_entry.insert(0, str(datetime.now().year))
        
        ctk.CTkLabel(month_frame, text="Месяц:").grid(row=0, column=2, padx=10, pady=10)
        self.month_entry = ctk.CTkEntry(month_frame, width=80, placeholder_text="1-12")
        self.month_entry.grid(row=0, column=3, padx=10, pady=10)
        self.month_entry.insert(0, str(datetime.now().month))
        
        load_btn = ctk.CTkButton(month_frame, text="🔄 Загрузить", command=self.load_month)
        load_btn.grid(row=0, column=4, padx=10, pady=10)
    
    def add_shift(self):
        date = self.date_entry.get().strip()
        hours_str = self.hours_entry.get().strip().replace(',', '.')
        rate_str = self.rate_entry.get().strip().replace(',', '.')
        note = self.note_entry.get().strip()
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
            hours = float(hours_str)
            rate = float(rate_str)
            
            if hours <= 0 or rate < 0:
                raise ValueError
            
            if upsert_shift(date, hours, rate, note):
                total = round(hours * rate, 2)
                messagebox.showinfo("Успех", f"✅ Смена за {date} сохранена!\nЗаработок: {total} ₽")
                self.hours_entry.delete(0, END)
                self.rate_entry.delete(0, END)
                self.note_entry.delete(0, END)
                self.load_current_month()
            else:
                messagebox.showerror("Ошибка", "❌ Не удалось сохранить данные.")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "❌ Проверьте формат:\n- Дата: ГГГГ-ММ-ДД\n- Часы и ставка: числа")
    
    def load_month(self):
        try:
            year = int(self.year_entry.get().strip())
            month = int(self.month_entry.get().strip())
            if not (1 <= month <= 12):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "❌ Введите корректный год и месяц (1-12)")
            return
        
        stats = get_monthly_stats(year, month)
        shifts = get_shifts_by_month(year, month)
        
        self.shifts_textbox.delete("1.0", END)
        
        header = f"📊 Итого за {month:02d}.{year}:\n"
        header += f"   Отработано часов: {stats['total_hours']:.1f}\n"
        header += f"   Заработано:       {stats['total_earnings']:,.2f} ₽\n\n"
        header += "📋 Детализация смен:\n"
        header += f"{'Дата':<12} | {'Часы':<6} | {'Ставка':<8} | {'Итого':<10} | {'Примечание'}\n"
        header += "-" * 68 + "\n"
        
        if shifts:
            for s in shifts:
                note_display = (s['note'][:12] + "...") if len(s['note'] or "") > 15 else (s['note'] or "-")
                header += f"{s['date']:<12} | {s['hours']:<6.1f} | {s['rate']:<8.2f} | {s['total']:<10.2f} | {note_display}\n"
        else:
            header += "\nℹ️ Смен за этот месяц не найдено.\n"
        
        self.shifts_textbox.insert("1.0", header)
    
    def load_current_month(self):
        self.year_entry.delete(0, END)
        self.month_entry.delete(0, END)
        self.year_entry.insert(0, str(datetime.now().year))
        self.month_entry.insert(0, str(datetime.now().month))
        self.load_month()

if __name__ == "__main__":
    init_db()
    app = ShiftTrackerApp()
    app.mainloop()
