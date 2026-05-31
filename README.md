# 🚀 Task Tracking App (Görev Takip Uygulaması)

Modern tasarıma sahip, bulut tabanlı ve interaktif takvim destekli bir masaüstü görev yönetim uygulaması. Python'ın modern arayüz kütüphanesi **CustomTkinter** ve güçlü bulut altyapısı **Supabase** (PostgreSQL & Storage) kullanılarak geliştirilmiştir.

---

## ✨ Özellikler

*   **☁️ Supabase Entegrasyonu:** Tüm görev verileriniz anlık olarak bulut veritabanında (PostgreSQL) saklanır.
*   **📁 Dosya ve Klasör Yükleme:** Görevlerinize PDF, görsel veya kaynak kod gibi dosyalar ekleyebilirsiniz. Klasör seçtiğinizde uygulama klasörü otomatik olarak `.zip` formatına dönüştürüp **Supabase Storage**'a yükler.
*   **📅 İnteraktif Takvim & Planlama:**
    *   Görevlerinizi ileri tarihe planlayabilirsiniz.
    *   Tarih seçimi yaparken manuel yazmak yerine şık **Açılır Takvim (Date Picker)** penceresini kullanabilirsiniz.
    *   Ana menüdeki takvimde görev olan günler **yeşil nokta** ile gösterilir, böylece arşivinizi kolayca filtreleyebilirsiniz.
*   **👥 Kişi Bazlı Gruplama:** Görevler listelenirken yükleyen kişilere (Uploader) göre otomatik olarak gruplandırılır.
*   **🛠️ Tam CRUD & Durum Yönetimi:**
    *   **Görev Ekleme:** Planlanan (Bekliyor) veya yapılmış iş (Tamamlandı) olarak görev kaydedebilme.
    *   **Düzenleme:** Görev başlıklarını anlık olarak güncelleyebilme.
    *   **Tamamlama:** Bekleyen görevleri tek tıkla tamamlayıp durumunu yeşil temaya çevirebilme.
    *   **Silme:** Görevi silerken dosyayı Supabase Storage'dan da otomatik olarak temizleyebilme.
*   **🎨 Modern Arayüz (Dark Mode):** Göz yormayan, dinamik renk geçişlerine ve premium hissettiren modern karanlık mod (Dark Mode) tasarımına sahiptir.

---

## 🚀 Teknolojiler

*   **Python 3.x**
*   **CustomTkinter** - Modern ve özelleştirilebilir Tkinter GUI bileşenleri.
*   **Supabase Python SDK** - Gerçek zamanlı veritabanı ve nesne depolama (Storage) yönetimi.
*   **Shutil & Tempfile** - Arka planda otomatik ZIP sıkıştırma işlemleri için.

---

