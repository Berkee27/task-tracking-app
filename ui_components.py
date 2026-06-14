import os
import webbrowser
from datetime import datetime
from collections import OrderedDict
import calendar

import customtkinter as ctk
from tkinter import filedialog


class UploadFrame(ctk.CTkFrame):
    """Görev yükleme formu."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.selected_file_path = None
        self.is_folder = False

        # ── Başlık ──
        self.header_label = ctk.CTkLabel(
            self, text="📤  Yeni Görev Yükle", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header_label.pack(pady=(20, 10))

        # ── Görev Başlığı ──
        self.title_label = ctk.CTkLabel(self, text="Görev Başlığı:")
        self.title_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Görev başlığını girin...", width=400)
        self.title_entry.pack(padx=30, pady=(2, 10))

        # ── Yükleyen Kişi Adı ──
        self.name_label = ctk.CTkLabel(self, text="Yükleyen Kişi:")
        self.name_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Adınızı girin...", width=400)
        self.name_entry.pack(padx=30, pady=(2, 10))

        # ── Görev Türü Seçimi ──
        self.type_label = ctk.CTkLabel(self, text="Görev Türü:")
        self.type_label.pack(anchor="w", padx=30, pady=(10, 0))

        self.task_type_seg = ctk.CTkSegmentedButton(
            self, values=["📅 Yeni Görev Planla", "✅ Yaptığım İşi Ekle"], width=400,
            command=self._on_type_change
        )
        self.task_type_seg.set("✅ Yaptığım İşi Ekle")  # Varsayılan
        self.task_type_seg.pack(padx=30, pady=(2, 10))

        # ── Planlanan Tarih ──
        self.date_label = ctk.CTkLabel(self, text="Tarih (GG.AA.YYYY) - Boş bırakılırsa bugün sayılır:")
        self.date_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.date_entry = ctk.CTkEntry(self.date_frame, placeholder_text="Örn: 05.06.2026", width=280)
        self.date_entry.pack(side="left", padx=(0, 10))
        self.date_btn = ctk.CTkButton(self.date_frame, text="📅 Seç", width=110, command=self._open_date_picker)
        self.date_btn.pack(side="left")
        # Sadece Planla seçiliyse gösterilmek üzere packlemeyi _on_type_change'de yapacağız.
        
        self.task_type_seg.set("✅ Yaptığım İşi Ekle")
        self._on_type_change("✅ Yaptığım İşi Ekle")

        # ── Dosya / Klasör Seçme Butonları ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(15, 2))

        self.file_button = ctk.CTkButton(
            btn_frame, text="📄  Dosya Seç", command=self._select_file, width=180
        )
        self.file_button.pack(side="left", padx=(0, 10))

        self.folder_button = ctk.CTkButton(
            btn_frame, text="📁  Klasör Seç", command=self._select_folder, width=180
        )
        self.folder_button.pack(side="left")

        self.file_label = ctk.CTkLabel(
            self,
            text="Henüz dosya veya klasör seçilmedi.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.file_label.pack(pady=(2, 10))

        # ── Gönder Butonu ──
        self.submit_button = ctk.CTkButton(
            self,
            text="🚀  Gönder",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
        )
        self.submit_button.pack(pady=(5, 5))

        # ── Durum Etiketi (yükleme geri bildirimi) ──
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="gray",
        )
        self.status_label.pack(pady=(5, 15))

    def _on_type_change(self, value):
        if "Planla" in value:
            self.date_label.pack(anchor="w", padx=30, pady=(10, 0))
            self.date_frame.pack(padx=30, pady=(2, 10), anchor="w")
        else:
            self.date_label.pack_forget()
            self.date_frame.pack_forget()

    def _open_date_picker(self):
        def on_date(date_tuple):
            y, m, d = date_tuple
            date_str = f"{d:02d}.{m:02d}.{y}"
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, date_str)
        DatePickerPopup(self, on_date)

    # ── Dosya seçme diyaloğu ──
    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Dosya Seçin",
            filetypes=[
                ("Tüm Dosyalar", "*.*"),
                ("ZIP Arşivleri", "*.zip"),
                ("PDF Dosyaları", "*.pdf"),
                ("Python Dosyaları", "*.py"),
                ("Resim Dosyaları", "*.png *.jpg *.jpeg"),
            ],
        )
        if path:
            self.selected_file_path = path
            self.is_folder = False
            short = os.path.basename(path)
            self.file_label.configure(text=f"✅  {short}", text_color="#2ecc71")

    # ── Klasör seçme diyaloğu ──
    def _select_folder(self):
        path = filedialog.askdirectory(title="Klasör Seçin")
        if path:
            self.selected_file_path = path
            self.is_folder = True
            short = os.path.basename(path)
            self.file_label.configure(
                text=f"✅  📁 {short}  (klasör — ZIP olarak yüklenecek)",
                text_color="#2ecc71",
            )

    def set_status(self, text: str, color: str = "gray"):
        self.status_label.configure(text=text, text_color=color)

    def get_data(self):
        title = self.title_entry.get().strip()
        name = self.name_entry.get().strip()
        file_path = self.selected_file_path
        date_str = self.date_entry.get().strip()
        
        selected_type = self.task_type_seg.get()
        if "Planla" in selected_type:
            status = "pending"
        else:
            status = "completed"
            
        return title, name, file_path, self.is_folder, status, date_str

    def clear_form(self):
        self.title_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.selected_file_path = None
        self.is_folder = False
        self.task_type_seg.set("✅ Yaptığım İşi Ekle")
        self._on_type_change("✅ Yaptığım İşi Ekle")
        self.file_label.configure(text="Henüz dosya veya klasör seçilmedi.", text_color="gray")


class CalendarFrame(ctk.CTkFrame):
    """Sol paneldeki interaktif takvim."""

    def __init__(self, master, on_date_select, **kwargs):
        super().__init__(master, **kwargs)
        self.on_date_select = on_date_select

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = None  # (year, month, day) or None (Tüm zamanlar)
        self.task_dates = set()    # İçinde görev olan günlerin kümesi: set of (year, month, day)

        self.months_tr = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
        }

        # ── Başlık ve Oklar ──
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 10))

        self.prev_btn = ctk.CTkButton(header_frame, text="<", width=30, command=self._prev_month)
        self.prev_btn.pack(side="left", padx=5)

        self.month_year_lbl = ctk.CTkLabel(
            header_frame, text="", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.month_year_lbl.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(header_frame, text=">", width=30, command=self._next_month)
        self.next_btn.pack(side="right", padx=5)

        # ── Gün İsimleri ──
        days_frame = ctk.CTkFrame(self, fg_color="transparent")
        days_frame.pack(fill="x", padx=5)
        days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        for i, day in enumerate(days):
            lbl = ctk.CTkLabel(days_frame, text=day, font=ctk.CTkFont(size=12, weight="bold"))
            lbl.grid(row=0, column=i, padx=4, pady=2)

        # ── Grid (Takvim Günleri) ──
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Tüm Zamanları Göster Butonu ──
        self.all_time_btn = ctk.CTkButton(
            self, text="Tüm Görevleri Göster", fg_color="#8e44ad", hover_color="#9b59b6",
            command=self._show_all_time
        )
        self.all_time_btn.pack(pady=10, fill="x", padx=10)

        self._build_calendar()

    def set_task_dates(self, task_dates: set):
        """Görev olan tarihleri güncelle ve takvimi yeniden çiz."""
        self.task_dates = task_dates
        self._build_calendar()

    def _prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self._build_calendar()

    def _next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self._build_calendar()

    def _show_all_time(self):
        self.selected_date = None
        self._build_calendar()
        self.on_date_select(None)

    def _build_calendar(self):
        self.month_year_lbl.configure(text=f"{self.months_tr[self.current_month]} {self.current_year}")

        # Eski butonları temizle
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        cal = calendar.monthcalendar(self.current_year, self.current_month)

        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue  # Boş gün

                current_date_tuple = (self.current_year, self.current_month, day)
                has_task = current_date_tuple in self.task_dates
                is_selected = current_date_tuple == self.selected_date

                # Renk belirleme
                if is_selected:
                    fg_color = "#3498db"  # Mavi (Seçili)
                    text_color = "white"
                elif has_task:
                    fg_color = "#2ecc71"  # Yeşil (Görev var)
                    text_color = "white"
                else:
                    fg_color = "transparent"
                    text_color = "gray" if ctk.get_appearance_mode() == "Dark" else "black"

                btn = ctk.CTkButton(
                    self.grid_frame,
                    text=str(day),
                    width=35,
                    height=35,
                    corner_radius=18,
                    fg_color=fg_color,
                    text_color=text_color,
                    hover_color="#2980b9" if is_selected else ("#27ae60" if has_task else "gray25"),
                    command=lambda d=day: self._on_day_click(d)
                )
                btn.grid(row=row_idx, column=col_idx, padx=3, pady=3)

    def _on_day_click(self, day):
        self.selected_date = (self.current_year, self.current_month, day)
        self._build_calendar()
        self.on_date_select(self.selected_date)


class ListFrame(ctk.CTkFrame):
    """Arşiv/Takvim görünümü ve Kişi bazlı görev listesi paneli."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.on_delete = None
        self.on_edit = None
        self.on_complete = None
        self.all_tasks = []
        self.selected_date = None

        # Ana layout: Sol (Takvim) ve Sağ (Görevler)
        self.grid_columnconfigure(0, weight=0)  # Sol sabit
        self.grid_columnconfigure(1, weight=1)  # Sağ genişleyebilir
        self.grid_rowconfigure(0, weight=1)

        # ── SOL PANEL: Takvim ──
        left_panel = ctk.CTkFrame(self, width=300)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Arşiv Başlığı
        archive_lbl = ctk.CTkLabel(left_panel, text="🗓️ Arşiv & Takvim", font=ctk.CTkFont(size=18, weight="bold"))
        archive_lbl.pack(pady=(15, 5))

        self.calendar = CalendarFrame(left_panel, on_date_select=self._filter_by_date)
        self.calendar.pack(fill="x", padx=10, pady=10)
        
        self.refresh_button = ctk.CTkButton(
            left_panel, text="🔄 Yenile", width=200, height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.refresh_button.pack(pady=20)


        # ── SAĞ PANEL: Görev Listesi ──
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.list_header_lbl = ctk.CTkLabel(
            right_panel, text="📋 Tüm Görevler", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.list_header_lbl.pack(pady=(10, 10), anchor="w")

        self.scrollable = ctk.CTkScrollableFrame(right_panel)
        self.scrollable.pack(fill="both", expand=True, pady=(0, 10))

    # ── Tarih İşlemleri ──
    @staticmethod
    def _parse_datetime_obj(created_at_str: str):
        try:
            dt_str = created_at_str.replace("Z", "+00:00")
            return datetime.fromisoformat(dt_str)
        except Exception:
            return None

    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        months_tr = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
        }
        return f"{dt.day} {months_tr[dt.month]} {dt.year} - {dt.strftime('%H:%M')}"

    def populate(self, tasks: list):
        """Veritabanından gelen görevleri yükler."""
        self.all_tasks = tasks
        
        # Takvimdeki yeşil noktalar için görev tarihlerini bul
        task_dates = set()
        for t in tasks:
            dt = self._parse_datetime_obj(t.get("created_at", ""))
            if dt:
                task_dates.add((dt.year, dt.month, dt.day))
        
        self.calendar.set_task_dates(task_dates)
        
        # Ekranı mevcut filtreye göre çiz
        self._render_tasks()

    def _filter_by_date(self, date_tuple):
        """Takvimden tarih seçildiğinde veya sıfırlandığında çağrılır."""
        self.selected_date = date_tuple
        self._render_tasks()

    def _render_tasks(self):
        """Görevleri filtreleyip kişiye göre gruplandırarak ekrana çizer."""
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        # Filtreleme
        filtered = []
        for task in self.all_tasks:
            dt = self._parse_datetime_obj(task.get("created_at", ""))
            if self.selected_date:
                # Eğer bir gün seçiliyse ve dt yoksa veya tarihler uyuşmuyorsa, atla.
                if not dt or (dt.year, dt.month, dt.day) != self.selected_date:
                    continue
            filtered.append(task)

        # Başlık güncelle
        months_tr = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 
                     7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
        if self.selected_date:
            y, m, d = self.selected_date
            self.list_header_lbl.configure(text=f"📋 Görevler: {d} {months_tr[m]} {y}")
        else:
            self.list_header_lbl.configure(text="📋 Tüm Görevler")

        if not filtered:
            empty_label = ctk.CTkLabel(
                self.scrollable, text="Bu tarihte görev bulunmuyor.", font=ctk.CTkFont(size=14), text_color="gray"
            )
            empty_label.pack(pady=40)
            return

        # Kişiye göre grupla (Uploader Name)
        grouped = OrderedDict()
        for task in filtered:
            name = task.get("uploader_name", "Bilinmiyor").strip().capitalize()
            grouped.setdefault(name, []).append(task)

        # Ekrana Çizdir
        for uploader, group_tasks in grouped.items():
            # Kişi Başlığı
            header = ctk.CTkLabel(
                self.scrollable,
                text=f"👤 {uploader}'nin Görevleri",
                font=ctk.CTkFont(size=17, weight="bold"),
                text_color="#f1c40f", # Sarımsı güzel bir renk
                anchor="w"
            )
            header.pack(fill="x", padx=5, pady=(20, 5))

            separator = ctk.CTkFrame(self.scrollable, height=2, fg_color="gray40")
            separator.pack(fill="x", padx=5, pady=(0, 10))

            for task in group_tasks:
                self._create_task_card(task)

    def _create_task_card(self, task: dict):
        """Tek bir görev kartı oluşturur."""
        task_id = task.get("id")
        file_url = task.get("file_url", "")
        task_title = task.get("title", "")
        status = task.get("status", "completed")  # Varsayılan eski veriler için completed

        # Durum ikonu
        title_prefix = "⏳ " if status == "pending" else "✅ "
        
        # Eğer pending ise hafif kırmızımsı border, completed ise standart border
        border_col = "#e67e22" if status == "pending" else "#2ecc71"
        
        card = ctk.CTkFrame(self.scrollable, corner_radius=10, border_width=2, border_color=border_col)
        card.pack(fill="x", padx=10, pady=5)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)

        title_color = "white" if status == "pending" else "#2ecc71"
        title_lbl = ctk.CTkLabel(
            info_frame, text=title_prefix + task_title, font=ctk.CTkFont(size=16, weight="bold"), anchor="w", text_color=title_color
        )
        title_lbl.pack(anchor="w")

        # Detaylı Tarih ve Saat
        dt = self._parse_datetime_obj(task.get("created_at", ""))
        time_str = self._format_datetime(dt) if dt else "Tarih bilinmiyor"
        
        status_text = "Bekliyor" if status == "pending" else "Tamamlandı"
        status_color = "gray" if status == "pending" else "#2ecc71"
        time_lbl = ctk.CTkLabel(
            info_frame, text=f"📅 Eklendiği Zaman: {time_str}  |  Durum: {status_text}", font=ctk.CTkFont(size=12), text_color=status_color, anchor="w"
        )
        time_lbl.pack(anchor="w", pady=(2, 0))

        # Sağ taraf butonları
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)

        # Tamamla butonu (sadece bekleyen görevler için)
        if status == "pending":
            complete_btn = ctk.CTkButton(
                btn_frame, text="✔️ Tamamla", width=100, height=32, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#2ecc71", hover_color="#27ae60",
                command=lambda furl=file_url: self._on_complete_click(furl)
            )
            complete_btn.pack(side="left", padx=(0, 10))

        # Eğer dosya varsa 'Aç' butonu koy, yoksa 'Metin Görevi' yaz
        if file_url and not file_url.startswith("no-file-"):
            open_btn = ctk.CTkButton(
                btn_frame, text="📂 Dosyayı Aç", width=100, height=32, font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda url=file_url: webbrowser.open(url)
            )
            open_btn.pack(side="left", padx=3)
        else:
            text_lbl = ctk.CTkLabel(
                btn_frame, text="📝 Dosya Yok", text_color="gray", font=ctk.CTkFont(size=12, slant="italic")
            )
            text_lbl.pack(side="left", padx=(0, 10))

        edit_btn = ctk.CTkButton(
            btn_frame, text="✏️", width=35, height=32, fg_color="#f39c12", hover_color="#e67e22",
            command=lambda furl=file_url, ttitle=task_title: self._on_edit_click(furl, ttitle)
        )
        edit_btn.pack(side="left", padx=3)

        delete_btn = ctk.CTkButton(
            btn_frame, text="🗑️", width=35, height=32, fg_color="#e74c3c", hover_color="#c0392b",
            command=lambda furl=file_url: self._on_delete_click(furl)
        )
        delete_btn.pack(side="left", padx=3)

    def _on_complete_click(self, file_url):
        if self.on_complete:
            self.on_complete(file_url)

    def _on_edit_click(self, file_url, current_title):
        if self.on_edit:
            self.on_edit(file_url, current_title)

    def _on_delete_click(self, file_url):
        if self.on_delete:
            self.on_delete(file_url)

class DatePickerPopup(ctk.CTkToplevel):
    def __init__(self, master, on_date_selected, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Tarih Seç")
        self.geometry("350x420")
        self.resizable(False, False)
        
        # Modal olması için
        self.transient(master)
        self.grab_set()
        
        self.on_date_selected = on_date_selected
        
        self.calendar = CalendarFrame(self, on_date_select=self._on_select)
        self.calendar.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Seçim yaparken 'Tüm Zamanlar' butonuna gerek yok, gizleyelim.
        self.calendar.all_time_btn.pack_forget()
        
    def _on_select(self, date_tuple):
        if date_tuple:
            self.on_date_selected(date_tuple)
            self.destroy()


# ==============================================================================
#                      ÇALIŞMA ODASI (STUDY ROOM) BİLEŞENİ
# ==============================================================================
import json
import threading
from datetime import datetime, timezone
from supabase_config import (
    get_or_create_user_status,
    toggle_user_study_status,
    heartbeat_user_status,
    get_all_users_status
)

def format_seconds(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def parse_iso_datetime(iso_str):
    if not iso_str:
        return None
    try:
        clean_str = iso_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception:
        return None


class StudyRoomFrame(ctk.CTkFrame):
    """Canlı Çalışma Odası ve Çalışma Süreleri Paneli."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app

        self.username = ""
        self.my_is_active = False
        self.my_today_study_time = 0  # saniye
        self.my_last_status_change = None  # datetime (UTC)

        self.heartbeat_counter = 0
        self.other_users_data = []
        self.user_cards = {}

        # Sol Panel (Profilim/Durumum) ve Sağ Panel (Çalışma Odası) oranları
        self.grid_columnconfigure(0, weight=0, minsize=380)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── SOL PANEL: Profil ve Durum Yönetimi ──
        self.left_panel = ctk.CTkFrame(self, width=360)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.left_header = ctk.CTkLabel(
            self.left_panel, text="🧘 Çalışma Profilim", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.left_header.pack(pady=(20, 10))

        # Kullanıcı Adı Ayarlama
        name_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        name_frame.pack(fill="x", padx=25, pady=5)

        name_lbl = ctk.CTkLabel(name_frame, text="Kullanıcı Adınız:")
        name_lbl.pack(anchor="w", padx=5)

        entry_btn_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
        entry_btn_frame.pack(fill="x", pady=5)

        self.username_entry = ctk.CTkEntry(
            entry_btn_frame, placeholder_text="Adınızı yazın...", width=200
        )
        self.username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.save_name_btn = ctk.CTkButton(
            entry_btn_frame, text="Kaydet", width=80, font=ctk.CTkFont(weight="bold"),
            command=self._on_save_username
        )
        self.save_name_btn.pack(side="right")

        # Canlı Durum Gösterge Kartı
        self.status_card = ctk.CTkFrame(
            self.left_panel, corner_radius=15, border_width=3, border_color="#e74c3c", fg_color="#2c3e50"
        )
        self.status_card.pack(fill="both", expand=True, padx=25, pady=(15, 20))

        self.status_dot = ctk.CTkLabel(
            self.status_card, text="●", text_color="#e74c3c", font=ctk.CTkFont(size=28)
        )
        self.status_dot.pack(pady=(20, 0))

        self.status_text_lbl = ctk.CTkLabel(
            self.status_card, text="MOLA VERİLİYOR", font=ctk.CTkFont(size=18, weight="bold"), text_color="#e74c3c"
        )
        self.status_text_lbl.pack(pady=5)

        duration_title = ctk.CTkLabel(
            self.status_card, text="Bugünkü Toplam Çalışma Süreniz:", font=ctk.CTkFont(size=13), text_color="gray"
        )
        duration_title.pack(pady=(25, 0))

        self.my_timer_lbl = ctk.CTkLabel(
            self.status_card, text="00:00:00", font=ctk.CTkFont(size=38, weight="bold", family="Courier New")
        )
        self.my_timer_lbl.pack(pady=10)

        # Başlat / Durdur Butonu
        self.toggle_study_btn = ctk.CTkButton(
            self.status_card,
            text="🟢 Çalışmaya Başla",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self._on_toggle_study,
            state="disabled"
        )
        self.toggle_study_btn.pack(fill="x", padx=30, pady=25)

        # ── SAĞ PANEL: Çalışma Odası Listesi ──
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        header_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=(15, 10), padx=10)

        self.right_header = ctk.CTkLabel(
            header_frame, text="👥 Çalışma Odasındakiler (Canlı)", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.right_header.pack(side="left")

        self.refresh_btn = ctk.CTkButton(
            header_frame, text="🔄 Yenile", width=90, height=30, font=ctk.CTkFont(size=12, weight="bold"),
            command=self._refresh_users_manual
        )
        self.refresh_btn.pack(side="right")

        self.scrollable = ctk.CTkScrollableFrame(self.right_panel)
        self.scrollable.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Zamanlayıcıları başlat
        self._tick_loop()
        self._auto_refresh_loop()

        # Kayıtlı kullanıcı adı varsa otomatik yükle
        self.after(100, self._load_saved_user)

    def _load_saved_user(self):
        saved_name = self.app.settings.get("username", "")
        if saved_name:
            self.username_entry.insert(0, saved_name)
            self._on_save_username()

    # ── KULLANICI AYARLARI ──
    def _on_save_username(self):
        name = self.username_entry.get().strip().capitalize()
        if not name:
            from tkinter import messagebox
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir kullanıcı adı girin.")
            return

        self.save_name_btn.configure(state="disabled", text="⏳...")
        self.username_entry.configure(state="disabled")

        # Supabase'den profil çekme işlemini arkaplanda çalıştır
        thread = threading.Thread(target=self._load_profile_worker, args=(name,))
        thread.daemon = True
        thread.start()

    def _load_profile_worker(self, name):
        try:
            profile = get_or_create_user_status(name)
            self.after(0, lambda: self._on_profile_loaded(name, profile))
        except Exception as e:
            self.after(0, lambda: self._on_profile_load_failed(str(e)))

    def _on_profile_loaded(self, name, profile):
        self.save_name_btn.configure(state="normal", text="Kaydet")
        self.username_entry.configure(state="normal")

        if not profile:
            from tkinter import messagebox
            messagebox.showerror("Hata", "Kullanıcı profili yüklenemedi.")
            return

        self.username = name
        self.app.save_username(name)  # Local settings'e kaydet

        self.my_is_active = profile.get("is_active", False)
        self.my_today_study_time = profile.get("today_study_time", 0)
        self.my_last_status_change = parse_iso_datetime(profile.get("last_status_change"))

        self.toggle_study_btn.configure(state="normal")
        self._update_my_status_ui()
        self._refresh_users_manual()

    def _on_profile_load_failed(self, err_msg):
        self.save_name_btn.configure(state="normal", text="Kaydet")
        self.username_entry.configure(state="normal")
        from tkinter import messagebox
        messagebox.showerror("Hata", f"Veritabanı bağlantı hatası:\n{err_msg}")

    # ── DURUM DEĞİŞTİRME (Çalışma Başlat/Durdur) ──
    def _on_toggle_study(self):
        if not self.username:
            return

        next_active = not self.my_is_active
        self.toggle_study_btn.configure(state="disabled", text="⏳ Güncelleniyor...")

        thread = threading.Thread(target=self._toggle_study_worker, args=(next_active,))
        thread.daemon = True
        thread.start()

    def _toggle_study_worker(self, next_active):
        try:
            profile = toggle_user_study_status(self.username, next_active)
            self.after(0, lambda: self._on_toggle_finished(profile, next_active))
        except Exception as e:
            self.after(0, lambda: self._on_toggle_failed(str(e)))

    def _on_toggle_finished(self, profile, next_active):
        self.toggle_study_btn.configure(state="normal")
        if not profile:
            from tkinter import messagebox
            messagebox.showerror("Hata", "Durum güncellenirken hata oluştu.")
            return

        self.my_is_active = profile.get("is_active", False)
        self.my_today_study_time = profile.get("today_study_time", 0)
        self.my_last_status_change = parse_iso_datetime(profile.get("last_status_change"))

        self.heartbeat_counter = 0
        self._update_my_status_ui()
        self._refresh_users_manual()

    def _on_toggle_failed(self, err_msg):
        self.toggle_study_btn.configure(state="normal")
        self._update_my_status_ui()
        from tkinter import messagebox
        messagebox.showerror("Hata", f"Bağlantı hatası:\n{err_msg}")

    def _update_my_status_ui(self):
        if self.my_is_active:
            # Aktif (Ders Çalışıyor) Görünümü
            self.status_card.configure(border_color="#2ecc71", fg_color="#1a3c26")
            self.status_dot.configure(text_color="#2ecc71")
            self.status_text_lbl.configure(text="DERS ÇALIŞIYOR", text_color="#2ecc71")
            self.toggle_study_btn.configure(
                text="🔴 Çalışmayı Durdur",
                fg_color="#e74c3c",
                hover_color="#c0392b"
            )
        else:
            # Pasif (Mola) Görünümü
            self.status_card.configure(border_color="#e74c3c", fg_color="#2c3e50")
            self.status_dot.configure(text_color="#e74c3c")
            self.status_text_lbl.configure(text="MOLA VERİLİYOR", text_color="#e74c3c")
            self.toggle_study_btn.configure(
                text="🟢 Çalışmaya Başla",
                fg_color="#2ecc71",
                hover_color="#27ae60"
            )

    # ── CANLI ZAMANLAYICI & KALP ATIŞI SÜRECİ ──
    def _tick_loop(self):
        self.after(1000, self._tick_loop)

        now_utc = datetime.now(timezone.utc)

        # 1. Kendi Sayacımı Güncelle
        if self.username:
            if self.my_is_active and self.my_last_status_change:
                elapsed = int((now_utc - self.my_last_status_change).total_seconds())
                if elapsed < 0:
                    elapsed = 0
                current_time = self.my_today_study_time + elapsed

                # Kalp Atışı (Her 30 saniyede bir veritabanına yedekle)
                self.heartbeat_counter += 1
                if self.heartbeat_counter >= 30:
                    self.heartbeat_counter = 0
                    self._send_heartbeat(elapsed)
            else:
                current_time = self.my_today_study_time

            self.my_timer_lbl.configure(text=format_seconds(current_time))

        # 2. Diğer Kullanıcıların Sayaçlarını Canlı Tıklat
        for user_data in self.other_users_data:
            other_name = user_data.get("username")
            if other_name == self.username:
                continue

            is_active = user_data.get("is_active", False)
            updated_at_str = user_data.get("updated_at")

            # Zaman aşımı kontrolü (2 dakika heartbeat gelmediyse pasif say)
            is_timed_out = False
            if is_active and updated_at_str:
                updated_at = parse_iso_datetime(updated_at_str)
                if updated_at:
                    diff = (now_utc - updated_at).total_seconds()
                    if diff > 120:
                        is_timed_out = True

            if is_active and not is_timed_out:
                last_change_str = user_data.get("last_status_change")
                last_change = parse_iso_datetime(last_change_str)
                today_time = user_data.get("today_study_time", 0)
                if last_change:
                    elapsed = int((now_utc - last_change).total_seconds())
                    if elapsed < 0:
                        elapsed = 0
                    current_time = today_time + elapsed
                else:
                    current_time = today_time
            else:
                current_time = user_data.get("today_study_time", 0)

            if other_name in self.user_cards:
                self.user_cards[other_name]["timer_lbl"].configure(text=format_seconds(current_time))
                if is_timed_out and user_data.get("is_active", False):
                    # Görsel olarak mola moduna çek
                    self.user_cards[other_name]["dot"].configure(text_color="#e74c3c")
                    self.user_cards[other_name]["status_lbl"].configure(
                        text="Mola Veriyor (Bağlantı Kesildi)", text_color="gray"
                    )
                    self.user_cards[other_name]["card"].configure(border_color="gray40")

    def _send_heartbeat(self, elapsed_seconds):
        if not self.username or elapsed_seconds <= 0:
            return
        thread = threading.Thread(target=self._heartbeat_worker, args=(elapsed_seconds,))
        thread.daemon = True
        thread.start()

    def _heartbeat_worker(self, elapsed_seconds):
        try:
            profile = heartbeat_user_status(self.username, elapsed_seconds)
            if profile:
                self.after(0, lambda: self._on_heartbeat_finished(profile))
        except Exception as e:
            print(f"Heartbeat DB save error: {e}")

    def _on_heartbeat_finished(self, profile):
        self.my_today_study_time = profile.get("today_study_time", 0)
        self.my_last_status_change = parse_iso_datetime(profile.get("last_status_change"))
        self.heartbeat_counter = 0

    def save_and_stop_study_sync(self):
        """Kapatılırken aktif süreyi veritabanına kaydeder (senkron)."""
        if self.username and self.my_is_active:
            print("Çalışma kaydediliyor ve sonlandırılıyor...")
            try:
                toggle_user_study_status(self.username, False)
            except Exception as e:
                print(f"Exit save error: {e}")

    # ── KULLANICI LİSTESİ ÇEKME & YENİLEME ──
    def _refresh_users_manual(self):
        self.refresh_btn.configure(state="disabled", text="⏳...")
        thread = threading.Thread(target=self._refresh_users_worker)
        thread.daemon = True
        thread.start()

    def _refresh_users_worker(self):
        try:
            users = get_all_users_status()
            self.after(0, lambda: self._on_users_refreshed(users))
        except Exception as e:
            print(f"Error fetching users: {e}")
            self.after(0, self._on_users_refresh_failed)

    def _on_users_refreshed(self, users):
        self.refresh_btn.configure(state="normal", text="🔄 Yenile")
        self.other_users_data = users
        self._render_users_list()

    def _on_users_refresh_failed(self):
        self.refresh_btn.configure(state="normal", text="🔄 Yenile")

    def _auto_refresh_loop(self):
        self.after(15000, self._auto_refresh_loop)
        if not self.username:
            return

        thread = threading.Thread(target=self._auto_refresh_worker)
        thread.daemon = True
        thread.start()

    def _auto_refresh_worker(self):
        try:
            users = get_all_users_status()
            self.after(0, lambda: self._on_users_refreshed_auto(users))
        except Exception as e:
            print(f"Auto refresh error: {e}")

    def _on_users_refreshed_auto(self, users):
        self.other_users_data = users
        self._render_users_list()

    def _render_users_list(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        self.user_cards = {}
        now_utc = datetime.now(timezone.utc)

        visible_users = self.other_users_data
        if not visible_users:
            empty_lbl = ctk.CTkLabel(
                self.scrollable, text="Çalışma odasında henüz kimse yok.", text_color="gray", font=ctk.CTkFont(size=14)
            )
            empty_lbl.pack(pady=40)
            return

        for user in visible_users:
            uname = user.get("username", "Bilinmeyen")
            is_me = (uname == self.username)

            is_active = user.get("is_active", False)
            updated_at_str = user.get("updated_at")

            is_timed_out = False
            if is_active and updated_at_str:
                updated_at = parse_iso_datetime(updated_at_str)
                if updated_at:
                    diff = (now_utc - updated_at).total_seconds()
                    if diff > 120:
                        is_timed_out = True

            if is_active and not is_timed_out:
                border_col = "#2ecc71"
                dot_col = "#2ecc71"
                status_text = "Çalışıyor..."
                status_text_color = "#2ecc71"

                last_change_str = user.get("last_status_change")
                last_change = parse_iso_datetime(last_change_str)
                today_time = user.get("today_study_time", 0)
                if last_change:
                    elapsed = int((now_utc - last_change).total_seconds())
                    if elapsed < 0:
                        elapsed = 0
                    current_time = today_time + elapsed
                else:
                    current_time = today_time
            else:
                border_col = "gray40"
                dot_col = "#e74c3c"
                status_text = "Mola Veriyor"
                if is_timed_out and is_active:
                    status_text = "Mola Veriyor (Bağlantı Kesildi)"
                status_text_color = "gray"
                current_time = user.get("today_study_time", 0)

            card_title = f"{uname} (Sen)" if is_me else uname
            card_title_color = "#f1c40f" if is_me else "white"

            card = ctk.CTkFrame(
                self.scrollable, corner_radius=10, border_width=2, border_color=border_col
            )
            card.pack(fill="x", padx=10, pady=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=8)

            name_dot_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            name_dot_frame.pack(anchor="w")

            dot = ctk.CTkLabel(
                name_dot_frame, text="●", text_color=dot_col, font=ctk.CTkFont(size=16)
            )
            dot.pack(side="left", padx=(0, 5))

            name_lbl = ctk.CTkLabel(
                name_dot_frame, text=card_title, font=ctk.CTkFont(size=15, weight="bold"), text_color=card_title_color
            )
            name_lbl.pack(side="left")

            status_lbl = ctk.CTkLabel(
                info_frame, text=status_text, font=ctk.CTkFont(size=12), text_color=status_text_color
            )
            status_lbl.pack(anchor="w", pady=(2, 0))

            timer_lbl = ctk.CTkLabel(
                card, text=format_seconds(current_time), font=ctk.CTkFont(size=20, weight="bold", family="Courier New")
            )
            timer_lbl.pack(side="right", padx=20)

            self.user_cards[uname] = {
                "card": card,
                "dot": dot,
                "name_lbl": name_lbl,
                "status_lbl": status_lbl,
                "timer_lbl": timer_lbl
            }
