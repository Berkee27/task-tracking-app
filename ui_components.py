import os
import webbrowser
from datetime import datetime
from collections import OrderedDict

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
        """Durum etiketini günceller."""
        self.status_label.configure(text=text, text_color=color)

    def get_data(self):
        """Form verilerini döndürür: (title, name, file_path, is_folder)"""
        title = self.title_entry.get().strip()
        name = self.name_entry.get().strip()
        file_path = self.selected_file_path
        return title, name, file_path, self.is_folder

    def clear_form(self):
        """Formu temizler."""
        self.title_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.selected_file_path = None
        self.is_folder = False
        self.file_label.configure(text="Henüz dosya veya klasör seçilmedi.", text_color="gray")


class ListFrame(ctk.CTkFrame):
    """Görevlerin tarih bazlı gruplanarak listelendiği panel."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Dışarıdan atanacak callback'ler
        self.on_delete = None   # (task_id, file_url) -> None
        self.on_edit = None     # (task_id, current_title) -> None

        # ── Üst bar: Başlık + Yenile ──
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))

        self.header_label = ctk.CTkLabel(
            top_bar, text="📋  Görev Listesi", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header_label.pack(side="left")

        self.refresh_button = ctk.CTkButton(
            top_bar, text="🔄 Yenile", width=100, height=30,
            font=ctk.CTkFont(size=12),
        )
        self.refresh_button.pack(side="right")

        # ── Scrollable alan ──
        self.scrollable = ctk.CTkScrollableFrame(self, width=500, height=400)
        self.scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ── Tarih parse yardımcısı ──
    @staticmethod
    def _parse_date(created_at_str: str) -> str:
        months_tr = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
        }
        try:
            dt_str = created_at_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str)
            return f"{dt.day} {months_tr[dt.month]} {dt.year}"
        except Exception:
            return "Tarih bilinmiyor"

    @staticmethod
    def _parse_time(created_at_str: str) -> str:
        try:
            dt_str = created_at_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%H:%M")
        except Exception:
            return ""

    def populate(self, tasks: list):
        """Görevleri tarihe göre gruplar ve kartlar halinde gösterir."""
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        if not tasks:
            empty_label = ctk.CTkLabel(
                self.scrollable,
                text="Henüz görev bulunmuyor.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            )
            empty_label.pack(pady=40)
            return

        # Tarihe göre grupla
        grouped = OrderedDict()
        for task in tasks:
            created_at = task.get("created_at", "")
            date_label = self._parse_date(created_at) if created_at else "Tarih bilinmiyor"
            grouped.setdefault(date_label, []).append(task)

        for date_label, group_tasks in grouped.items():
            # Tarih başlığı
            date_header = ctk.CTkLabel(
                self.scrollable,
                text=f"📅  {date_label}",
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w",
            )
            date_header.pack(fill="x", padx=5, pady=(15, 5))

            separator = ctk.CTkFrame(self.scrollable, height=2, fg_color="gray40")
            separator.pack(fill="x", padx=5, pady=(0, 8))

            for task in group_tasks:
                self._create_task_card(task)

    def _create_task_card(self, task: dict):
        """Tek bir görev kartı oluşturur."""
        card = ctk.CTkFrame(self.scrollable, corner_radius=10)
        card.pack(fill="x", padx=5, pady=4)

        # Sol taraf: bilgiler
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)

        title_lbl = ctk.CTkLabel(
            info_frame,
            text=task.get("title", "Başlıksız"),
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        title_lbl.pack(anchor="w")

        uploader_lbl = ctk.CTkLabel(
            info_frame,
            text=f"👤 {task.get('uploader_name', 'Bilinmiyor')}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        uploader_lbl.pack(anchor="w")

        # Saat bilgisi
        created_at = task.get("created_at", "")
        time_str = self._parse_time(created_at)
        if time_str:
            time_lbl = ctk.CTkLabel(
                info_frame,
                text=f"🕐 {time_str}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w",
            )
            time_lbl.pack(anchor="w")

        # Sağ taraf: butonlar
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)

        task_id = task.get("id")
        file_url = task.get("file_url", "")
        task_title = task.get("title", "")

        # Dosyayı Aç
        open_btn = ctk.CTkButton(
            btn_frame,
            text="📂 Aç",
            width=70,
            height=30,
            font=ctk.CTkFont(size=12),
            command=lambda url=file_url: webbrowser.open(url),
        )
        open_btn.pack(side="left", padx=2)

        # Düzenle
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            width=35,
            height=30,
            fg_color="#f39c12",
            hover_color="#e67e22",
            font=ctk.CTkFont(size=14),
            command=lambda tid=task_id, ttitle=task_title: self._on_edit_click(tid, ttitle),
        )
        edit_btn.pack(side="left", padx=2)

        # Sil
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=35,
            height=30,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            font=ctk.CTkFont(size=14),
            command=lambda tid=task_id, furl=file_url: self._on_delete_click(tid, furl),
        )
        delete_btn.pack(side="left", padx=2)

    def _on_edit_click(self, task_id, current_title):
        if self.on_edit:
            self.on_edit(task_id, current_title)

    def _on_delete_click(self, task_id, file_url):
        if self.on_delete:
            self.on_delete(task_id, file_url)
