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
        return title, name, file_path, self.is_folder

    def clear_form(self):
        self.title_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.selected_file_path = None
        self.is_folder = False
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
        card = ctk.CTkFrame(self.scrollable, corner_radius=10, border_width=1, border_color="gray30")
        card.pack(fill="x", padx=10, pady=5)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)

        title_lbl = ctk.CTkLabel(
            info_frame, text=task.get("title", "Başlıksız"), font=ctk.CTkFont(size=16, weight="bold"), anchor="w"
        )
        title_lbl.pack(anchor="w")

        # Detaylı Tarih ve Saat
        dt = self._parse_datetime_obj(task.get("created_at", ""))
        time_str = self._format_datetime(dt) if dt else "Tarih bilinmiyor"
        
        time_lbl = ctk.CTkLabel(
            info_frame, text=f"📅 Eklendiği Zaman: {time_str}", font=ctk.CTkFont(size=12), text_color="gray", anchor="w"
        )
        time_lbl.pack(anchor="w", pady=(2, 0))

        # Sağ taraf butonları
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)

        file_url = task.get("file_url", "")
        task_title = task.get("title", "")

        open_btn = ctk.CTkButton(
            btn_frame, text="📂 Dosyayı Aç", width=100, height=32, font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda url=file_url: webbrowser.open(url)
        )
        open_btn.pack(side="left", padx=3)

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

    def _on_edit_click(self, file_url, current_title):
        if self.on_edit:
            self.on_edit(file_url, current_title)

    def _on_delete_click(self, file_url):
        if self.on_delete:
            self.on_delete(file_url)
