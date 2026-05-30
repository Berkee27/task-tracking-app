import os
import shutil
import tempfile
import threading
import customtkinter as ctk
from tkinter import messagebox

from supabase_config import upload_task, get_all_tasks, delete_task, update_task
from ui_components import UploadFrame, ListFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Pencere ayarları ──
        self.title("Task Tracking App")
        self.geometry("800x600")
        self.minsize(700, 500)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Tab View ──
        self.tabview = ctk.CTkTabview(self, width=760, height=560)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tabview.add("Görev Yükle")
        self.tabview.add("Görevler")

        # ── Upload Frame ──
        self.upload_frame = UploadFrame(self.tabview.tab("Görev Yükle"))
        self.upload_frame.pack(fill="both", expand=True)
        self.upload_frame.submit_button.configure(command=self._on_submit)

        # ── List Frame ──
        self.list_frame = ListFrame(self.tabview.tab("Görevler"))
        self.list_frame.pack(fill="both", expand=True)
        # Callback'leri bağla
        self.list_frame.on_delete = self._on_delete
        self.list_frame.on_edit = self._on_edit
        self.list_frame.refresh_button.configure(command=self._refresh_tasks)

        # ── Sekme değişikliğinde listeyi güncelle ──
        self.tabview.configure(command=self._on_tab_change)

        # ── İlk açılışta görev listesini yükle ──
        self._refresh_tasks()

    # ══════════════════════════ YÜKLEME ══════════════════════════
    def _on_submit(self):
        title, name, file_path, is_folder = self.upload_frame.get_data()

        # Doğrulama
        if not title:
            messagebox.showwarning("Uyarı", "Lütfen görev başlığını girin.")
            return
        if not name:
            messagebox.showwarning("Uyarı", "Lütfen adınızı girin.")
            return
        if not file_path:
            messagebox.showwarning("Uyarı", "Lütfen bir dosya veya klasör seçin.")
            return

        # Butonu devre dışı bırak + durum göster
        self.upload_frame.submit_button.configure(state="disabled", text="⏳ Yükleniyor...")
        self.upload_frame.set_status("⏳ Dosya yükleniyor, lütfen bekleyin...", "#f39c12")

        thread = threading.Thread(
            target=self._upload_worker, args=(title, file_path, name, is_folder)
        )
        thread.daemon = True
        thread.start()

    def _upload_worker(self, title, file_path, name, is_folder):
        temp_zip = None
        try:
            actual_path = file_path

            if is_folder:
                folder_name = os.path.basename(file_path)
                temp_dir = tempfile.mkdtemp()
                zip_base = os.path.join(temp_dir, folder_name)
                temp_zip = shutil.make_archive(zip_base, "zip", file_path)
                actual_path = temp_zip

            upload_task(title, actual_path, name)
            self.after(0, self._upload_success)

        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._upload_error(error_msg))
        finally:
            if temp_zip and os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                    os.rmdir(os.path.dirname(temp_zip))
                except Exception:
                    pass

    def _upload_success(self):
        self.upload_frame.submit_button.configure(state="normal", text="🚀  Gönder")
        self.upload_frame.set_status("✅ Görev başarıyla yüklendi!", "#2ecc71")
        self.upload_frame.clear_form()
        messagebox.showinfo("Başarılı", "Görev başarıyla yüklendi! ✅")
        # 5 saniye sonra durum mesajını temizle
        self.after(5000, lambda: self.upload_frame.set_status(""))
        self._refresh_tasks()

    def _upload_error(self, error_msg):
        self.upload_frame.submit_button.configure(state="normal", text="🚀  Gönder")
        self.upload_frame.set_status(f"❌ Yükleme başarısız!", "#e74c3c")
        messagebox.showerror("Hata", f"Yükleme sırasında bir hata oluştu:\n{error_msg}")
        self.after(5000, lambda: self.upload_frame.set_status(""))

    # ══════════════════════════ SİLME ══════════════════════════
    def _on_delete(self, task_id, file_url):
        confirm = messagebox.askyesno(
            "Silme Onayı",
            "Bu görevi silmek istediğinize emin misiniz?\n\n"
            "Bu işlem geri alınamaz. Dosya ve kayıt kalıcı olarak silinecektir.",
        )
        if not confirm:
            return

        thread = threading.Thread(
            target=self._delete_worker, args=(task_id, file_url)
        )
        thread.daemon = True
        thread.start()

    def _delete_worker(self, task_id, file_url):
        try:
            delete_task(task_id, file_url)
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
    def _on_edit(self, task_id, current_title):
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
            target=self._edit_worker, args=(task_id, new_title)
        )
        thread.daemon = True
        thread.start()

    def _edit_worker(self, task_id, new_title):
        try:
            update_task(task_id, new_title)
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

    def _refresh_tasks(self):
        try:
            tasks = get_all_tasks()
            self.list_frame.populate(tasks)
        except Exception as e:
            print(f"Görevler yüklenirken hata: {e}")

    # ══════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    app = App()
    app.mainloop()
