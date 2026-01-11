# 📚 KitapKurdu (BookWorm)

**Veri Tabanı Destekli E-Ticaret Projesi**
---

## 🚀 Proje Hakkında
Bu proje, Python **Django** framework'ü ve **Microsoft SQL Server (MSSQL)** kullanılarak geliştirilmiş, uçtan uca bir kitap satış ve e-ticaret uygulamasıdır. 

Sistem, sadece web arayüzü sunmakla kalmayıp; **Stored Procedures, Triggers ve Views** gibi ileri seviye veritabanı nesneleriyle veri bütünlüğünü ve iş mantığını backend tarafında garanti altına almaktadır.

---

## 📂 Klasör Yapısı
* **`/KitapKurdu`**: Django kaynak kodlarını içerir (manage.py, apps, settings vb.).
* **`/Database`**: Veritabanı kurulum scriptlerini içerir.
    * `01_Database_Setup.sql`: Tablo kurulumları
    * `02_SQL_Objects.sql`: SP, Trigger ve View'lar
    * `03_Data_Insert.sql`: Örnek veriler
* **`Report`**: Proje rapor dosyası.

---

## 🛠️ Kurulum ve Çalıştırma Rehberi

Projenin sorunsuz çalışması için aşağıdaki adımları sırasıyla uygulayınız.

### Adım 1: Veritabanı Kurulumu (SQL Server)
1. Microsoft SQL Server Management Studio (SSMS) uygulamasını açın.
2. **`Database`** klasörü içindeki `.sql` dosyalarını **sırasıyla** çalıştırın:
    * 1️⃣ `01_Database_Setup.sql` (Tabloları oluşturur)
    * 2️⃣ `02_SQL_Objects.sql` (Fonksiyonları ve prosedürleri ekler)
    * 3️⃣ `03_Data_Insert.sql` (Test verilerini yükler)

### Adım 2: Python Ortamının Hazırlanması
Terminali açın ve proje dizinine gelerek sanal ortamı kurun:

```bash
# Sanal ortamı oluştur
python -m venv venv

# Sanal ortamı aktif et (Windows için)
venv\Scripts\activate

# Gerekli kütüphaneleri yükle
pip install django pyodbc django-mssql-backend
