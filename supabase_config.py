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


def get_today_date_str():
    from datetime import date
    return date.today().isoformat()


def get_or_create_user_status(username: str):
    """
    Kullanıcının durumunu getirir. Eğer yoksa oluşturur.
    Gün değiştiyse bugünün tarihine günceller ve bugünkü süreyi 0 yapar.
    """
    from datetime import datetime, timezone
    username = username.strip().capitalize()
    if not username:
        return None
        
    try:
        res = supabase.table("user_status").select("*").eq("username", username).execute()
        today_str = get_today_date_str()
        
        if not res.data:
            # Kullanıcı yok, yeni kayıt aç
            new_data = {
                "username": username,
                "is_active": False,
                "today_study_time": 0,
                "last_status_change": datetime.now(timezone.utc).isoformat(),
                "last_active_date": today_str,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            supabase.table("user_status").insert(new_data).execute()
            return new_data
        
        user_data = res.data[0]
        db_date_str = user_data.get("last_active_date")
        
        # Gün değiştiyse sıfırla
        if db_date_str != today_str:
            user_data["today_study_time"] = 0
            user_data["is_active"] = False
            user_data["last_active_date"] = today_str
            user_data["last_status_change"] = datetime.now(timezone.utc).isoformat()
            user_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # DB'de güncelle
            supabase.table("user_status").update({
                "today_study_time": 0,
                "is_active": False,
                "last_active_date": today_str,
                "last_status_change": user_data["last_status_change"],
                "updated_at": user_data["updated_at"]
            }).eq("username", username).execute()
            
        return user_data
    except Exception as e:
        print(f"Error in get_or_create_user_status: {e}")
        return None


def toggle_user_study_status(username: str, start_study: bool):
    """
    Kullanıcının ders çalışma durumunu başlatır veya durdurur.
    """
    from datetime import datetime, timezone
    username = username.strip().capitalize()
    if not username:
        return None
        
    # Önce güncel veriyi al (böylece gün aşımı kontrol edilir)
    user_data = get_or_create_user_status(username)
    if not user_data:
        return None
        
    now_utc = datetime.now(timezone.utc)
    now_utc_str = now_utc.isoformat()
    today_str = get_today_date_str()
    
    is_active = user_data.get("is_active", False)
    today_study_time = user_data.get("today_study_time", 0)
    last_status_change_str = user_data.get("last_status_change")
    
    if start_study:
        # Pasiften aktife geçiş veya aktif kalmaya zorlama
        new_data = {
            "is_active": True,
            "last_status_change": now_utc_str,
            "last_active_date": today_str,
            "updated_at": now_utc_str
        }
        res = supabase.table("user_status").update(new_data).eq("username", username).execute()
        if res.data:
            return res.data[0]
    else:
        if is_active:
            # Aktiften pasife geçiş. Geçen süreyi hesapla.
            try:
                clean_ts = last_status_change_str.replace("Z", "+00:00")
                last_change = datetime.fromisoformat(clean_ts)
                elapsed = int((now_utc - last_change).total_seconds())
                if elapsed < 0:
                    elapsed = 0
            except Exception as e:
                print(f"Time parsing error: {e}")
                elapsed = 0
            
            new_study_time = today_study_time + elapsed
            new_data = {
                "is_active": False,
                "today_study_time": new_study_time,
                "last_status_change": now_utc_str,
                "last_active_date": today_str,
                "updated_at": now_utc_str
            }
            res = supabase.table("user_status").update(new_data).eq("username", username).execute()
            if res.data:
                return res.data[0]
        else:
            # Zaten pasif
            return user_data
            
    return None


def heartbeat_user_status(username: str, elapsed_seconds: int):
    """
    Aktif kullanıcının süresini arkaplanda periyodik olarak veritabanına kaydeder (kalp atışı).
    """
    from datetime import datetime, timezone
    username = username.strip().capitalize()
    if not username or elapsed_seconds <= 0:
        return None
        
    try:
        # Önce veriyi çekelim
        user_data = get_or_create_user_status(username)
        if not user_data:
            return None
            
        today_study_time = user_data.get("today_study_time", 0)
        new_study_time = today_study_time + elapsed_seconds
        
        now_utc = datetime.now(timezone.utc)
        now_utc_str = now_utc.isoformat()
        
        new_data = {
            "today_study_time": new_study_time,
            "last_status_change": now_utc_str,
            "updated_at": now_utc_str,
            "is_active": True
        }
        
        res = supabase.table("user_status").update(new_data).eq("username", username).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        print(f"Error in heartbeat: {e}")
    return None


def get_all_users_status():
    """
    Tüm kullanıcıların durumlarını getirir.
    """
    try:
        res = supabase.table("user_status").select("*").order("is_active", desc=True).order("today_study_time", desc=True).execute()
        return res.data
    except Exception as e:
        print(f"Error in get_all_users_status: {e}")
        return []