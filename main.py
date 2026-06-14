import os
import json
import shutil
import tempfile
import threading
import customtkinter as ctk
from tkinter import messagebox

from supabase_config import upload_task, get_all_tasks, delete_task, update_task
from ui_components import UploadFrame, ListFrame, StudyRoomFrame



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Settings ──
        self.settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = self._load_settings()

        # ── Pencere ayarları ──
        self.title("Task Tracking App")
        self.geometry("1100x700")
        self.minsize(900, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Tab View ──
        self.tabview = ctk.CTkTabview(self, width=760, height=560)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tabview.add("Çalışma Odası")
        self.tabview.add("Görev Yükle")
        self.tabview.add("Görevler")

        # ── Study Room Frame ──
        self.study_room_frame = StudyRoomFrame(self.tabview.tab("Çalışma Odası"), self)
        self.study_room_frame.pack(fill="both", expand=True)

        # ── Upload Frame ──
        self.upload_frame = UploadFrame(self.tabview.tab("Görev Yükle"))
        self.upload_frame.pack(fill="both", expand=True)
        self.upload_frame.submit_button.configure(command=self._on_submit)

        # Pre-fill name if it was saved in settings
        saved_name = self.settings.get("username", "")
        if saved_name:
            self.upload_frame.name_entry.insert(0, saved_name)

        # ── List Frame ──
        self.list_frame = ListFrame(self.tabview.tab("Görevler"))
        self.list_frame.pack(fill="both", expand=True)
        # Callback'leri bağla
        self.list_frame.on_delete = self._on_delete
        self.list_frame.on_edit = self._on_edit
        self.list_frame.on_complete = self._on_complete
        self.list_frame.refresh_button.configure(command=self._refresh_tasks)

        # ── Sekme değişikliğinde listeyi güncelle ──
        self.tabview.configure(command=self._on_tab_change)

        # ── Kapatma İşlemi Protokolü ──
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # ── İlk açılışta görev listesini yükle ──
        self._refresh_tasks()

    # ══════════════════════════ YÜKLEME ══════════════════════════
    def _on_submit(self):
        title, name, file_path, is_folder, status, date_str = self.upload_frame.get_data()

        # Doğrulama
        if not title:
            messagebox.showwarning("Uyarı", "Lütfen görev başlığını girin.")
            return
        if not name:
            messagebox.showwarning("Uyarı", "Lütfen adınızı girin.")
            return

        # Butonu devre dışı bırak + durum göster
        self.upload_frame.submit_button.configure(state="disabled", text="⏳ Yükleniyor...")
        self.upload_frame.set_status("Dosya hazırlanıyor...", "orange")

        # İşlemi arkaplan thread'ine at (GUI donmasın)
        thread = threading.Thread(
            target=self._upload_worker, args=(title, file_path, name, is_folder, status, date_str)
        )
        thread.daemon = True
        thread.start()

    def _upload_worker(self, title, file_path, name, is_folder, status, date_str):
        try:
            if is_folder and file_path:
                self.upload_frame.set_status("Klasör ZIP yapılıyor...", "orange")
                # Geçici dizinde ZIP oluştur
                temp_dir = tempfile.gettempdir()
                zip_filename = os.path.basename(file_path)
                zip_path = os.path.join(temp_dir, zip_filename)
                
                shutil.make_archive(zip_path, 'zip', file_path)
                file_path = zip_path + ".zip"

            self.upload_frame.set_status("Supabase'e yükleniyor...", "orange")
            upload_task(title, file_path, name, status, date_str)

            # Başarılı dönüşü ana thread'de yap
            self.after(0, self._upload_success)

        except Exception as e:
            # Hata mesajını değişkene alıp ana thread'e iletiyoruz
            error_msg = str(e)
            self.after(0, lambda: self._upload_error(error_msg))

    def _upload_success(self):
        self.upload_frame.submit_button.configure(state="normal", text="🚀 Gönder")
        self.upload_frame.set_status("✅ Görev başarıyla eklendi!", "green")
        self.upload_frame.clear_form()
        
        # Görevler sekmesini yenile ve o sekmeye geç
        self._refresh_tasks()
        self.tabview.set("Görevler")
        self.after(5000, lambda: self.upload_frame.set_status(""))

    def _upload_error(self, error_msg):
        self.upload_frame.submit_button.configure(state="normal", text="🚀  Gönder")
        self.upload_frame.set_status(f"❌ Yükleme başarısız!", "#e74c3c")
        messagebox.showerror("Hata", f"Yükleme sırasında bir hata oluştu:\n{error_msg}")

    # ══════════════════════════ TAMAMLA ══════════════════════════
    def _on_complete(self, file_url):
        thread = threading.Thread(
            target=self._complete_worker, args=(file_url,)
        )
        thread.daemon = True
        thread.start()

    def _complete_worker(self, file_url):
        try:
            from supabase_config import complete_task
            complete_task(file_url)
            self.after(0, self._complete_success)
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._complete_error(error_msg))

    def _complete_success(self):
        messagebox.showinfo("Başarılı", "Görev başarıyla tamamlandı! ✅")
        self._refresh_tasks()

    def _complete_error(self, error_msg):
        messagebox.showerror("Hata", f"Görev güncellenirken hata oluştu:\n{error_msg}")

    # ══════════════════════════ SİLME ══════════════════════════
    def _on_delete(self, file_url):
        confirm = messagebox.askyesno(
            "Silme Onayı",
            "Bu görevi silmek istediğinize emin misiniz?\n\n"
            "Bu işlem geri alınamaz. Dosya ve kayıt kalıcı olarak silinecektir.",
        )
        if not confirm:
            return

        thread = threading.Thread(
            target=self._delete_worker, args=(file_url,)
        )
        thread.daemon = True
        thread.start()

    def _delete_worker(self, file_url):
        try:
            delete_task(file_url)
            self.after(0, self._delete_success)
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._delete_error(error_msg))

    def _delete_success(self):
        messagebox.showinfo("Başarılı", "Görev başarıyla silindi! 🗑️")
        self._refresh_tasks()

    def _delete_error(self, error_msg):
        messagebox.showerror("Hata", f"Silme sırasında hata oluştu:\n{error_msg}")

    # ══════════════════════════ DÜZENLEME ══════════════════════════
    def _on_edit(self, file_url, current_title):
        dialog = ctk.CTkInputDialog(
            text="Yeni görev başlığını girin:",
            title="Görevi Düzenle",
        )
        # Mevcut başlığı gösteremiyoruz (CTkInputDialog sınırlı), ama kullanıcı yeni başlık yazacak
        new_title = dialog.get_input()

        if not new_title or not new_title.strip():
            return  # İptal edildi veya boş bırakıldı

        new_title = new_title.strip()

        thread = threading.Thread(
            target=self._edit_worker, args=(file_url, new_title)
        )
        thread.daemon = True
        thread.start()

    def _edit_worker(self, file_url, new_title):
        try:
            update_task(file_url, new_title)
            self.after(0, self._edit_success)
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._edit_error(error_msg))

    def _edit_success(self):
        messagebox.showinfo("Başarılı", "Görev başlığı güncellendi! ✏️")
        self._refresh_tasks()

    def _edit_error(self, error_msg):
        messagebox.showerror("Hata", f"Düzenleme sırasında hata oluştu:\n{error_msg}")

    # ══════════════════════════ GÖREV LİSTESİ ══════════════════════════
    def _on_tab_change(self):
        if self.tabview.get() == "Görevler":
            self._refresh_tasks()
        elif self.tabview.get() == "Çalışma Odası":
            if hasattr(self, "study_room_frame"):
                self.study_room_frame._refresh_users_manual()

    def _refresh_tasks(self):
        try:
            tasks = get_all_tasks()
            self.list_frame.populate(tasks)
        except Exception as e:
            print(f"Görevler yüklenirken hata: {e}")

    # ══════════════════════════ AYARLAR VE KAPATMA ══════════════════════════
    def _load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"username": ""}

    def save_username(self, username):
        self.settings["username"] = username
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Settings save error: {e}")
            
        if hasattr(self, "upload_frame"):
            self.upload_frame.name_entry.delete(0, "end")
            self.upload_frame.name_entry.insert(0, username)

    def _on_closing(self):
        # Kapatılırken çalışan süreyi kaydet
        if hasattr(self, "study_room_frame"):
            self.study_room_frame.save_and_stop_study_sync()
        self.destroy()

    # ══════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    app = App()
    app.mainloop()
