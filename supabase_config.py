import os
import time
from urllib.parse import urlparse
from supabase import create_client, Client

# URL'ni senin için hazırladım
SUPABASE_URL = "https://oavvdidpuhzszuphkebg.supabase.co"

# Aşağıdaki tırnak içine kopyaladığın sb_publishable_ ile başlayan anahtarı yapıştır
SUPABASE_KEY = "sb_publishable_bxlHeKfaKaSKFhhqtG-Cgw_Gus70BBE" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_task(title: str, file_path: str, uploader_name: str, status: str = "completed", date_str: str = ""):
    """
    Dosya/Klasör seçildiyse Supabase Storage'a yükler ve URL'sini alır.
    Seçilmediyse sadece başlık, yükleyen adını ve durumu tasks tablosuna kaydeder.
    """
    file_url = ""

    # Eğer bir dosya yolu geldiyse Storage'a yükle
    if file_path:
        with open(file_path, "rb") as f:
            file_data = f.read()

        original_name = os.path.basename(file_path)
        timestamp = int(time.time())
        storage_filename = f"{timestamp}_{original_name}"

        try:
            supabase.storage.from_("task-files").upload(
                path=storage_filename,
                file=file_data,
                file_options={"content-type": "application/octet-stream"},
            )
            # URL'yi al
            file_url = supabase.storage.from_("task-files").get_public_url(storage_filename)
        except Exception as e:
            error_str = str(e)
            if "row-level security" in error_str.lower() or "unauthorized" in error_str.lower():
                raise Exception(
                    "Storage RLS hatası!\n\n"
                    "Supabase Dashboard → Storage → task-files → Policies bölümüne gidin\n"
                    "ve aşağıdaki politikaları ekleyin:\n\n"
                    "• INSERT için: allow all (herkese izin ver)\n"
                    "• SELECT için: allow all (herkese izin ver)\n"
                    "• DELETE için: allow all (herkese izin ver)"
                ) from e
            raise Exception(f"Dosya yükleme hatası: {error_str}") from e

    # Görev bilgilerini veritabanına kaydet (file_url boşsa benzersiz bir id üret)
    import uuid
    if not file_url:
        file_url = f"no-file-{uuid.uuid4()}"

    task_data = {
        "title": title,
        "file_url": file_url,
        "uploader_name": uploader_name,
        "status": status,
    }

    if date_str:
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%d.%m.%Y")
            task_data["created_at"] = dt.isoformat() + "Z"
        except Exception as e:
            raise Exception(f"Tarih formatı hatalı (GG.AA.YYYY olmalı): {e}")

    supabase.table("tasks").insert(task_data).execute()

    return True


def get_all_tasks():
    """
    tasks tablosundaki tüm görevleri created_at sütununa göre
    azalan sırada (en yeni en üstte) döndürür.
    created_at sütunu henüz yoksa sırasız olarak döndürür.
    """
    try:
        response = (
            supabase.table("tasks")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception:
        pass

    # created_at sütunu henüz eklenmemişse sırasız getir
    response = (
        supabase.table("tasks")
        .select("*")
        .execute()
    )
    return response.data


def delete_task(file_url: str):
    """
    Görevi veritabanından ve dosyasını Storage'dan siler.
    Silme işlemini benzersiz olan file_url üzerinden yapar.
    """
    try:
        parsed = urlparse(file_url)
        path_parts = parsed.path.split("/")
        if "task-files" in path_parts:
            idx = path_parts.index("task-files")
            storage_filename = "/".join(path_parts[idx + 1:])
            supabase.storage.from_("task-files").remove([storage_filename])
    except Exception as e:
        print(f"Storage silme hatası (devam ediliyor): {e}")

    # Veritabanından sil (id olmadığı için file_url ile bulup siliyoruz)
    supabase.table("tasks").delete().eq("file_url", file_url).execute()


def update_task(file_url: str, new_title: str):
    """
    Görevin başlığını file_url kullanarak günceller.
    """
    supabase.table("tasks").update(
        {"title": new_title}
    ).eq("file_url", file_url).execute()


def complete_task(file_url: str):
    """
    Görevi tamamlandı olarak işaretler (status='completed').
    """
    res = supabase.table("tasks").update(
        {"status": "completed"}
    ).eq("file_url", file_url).execute()
    
    if not res.data:
        raise Exception("Güncelleme yapılamadı. (Belki görev bulunamadı veya yetki yok)")