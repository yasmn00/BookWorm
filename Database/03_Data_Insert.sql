USE KitapKurduDB;
GO

-- =============================================
-- 1. INSERT CATEGORIES
-- =============================================
IF NOT EXISTS (SELECT 1 FROM Categories)
BEGIN
    INSERT INTO Categories (CategoryName) VALUES 
    ('Roman'),                 -- ID: 1
    ('Felsefe'),               -- ID: 2
    ('Çizgi Roman ve Manga'),  -- ID: 3
    ('Çocuk'),                 -- ID: 4
    ('Geliþim');               -- ID: 5
    
    PRINT '>>> Categories inserted.';
END
GO

-- =============================================
-- 2. INSERT USERS
-- =============================================
IF NOT EXISTS (SELECT 1 FROM Users)
BEGIN
    INSERT INTO Users (FullName, Email, PasswordHash, UserType) VALUES 
    ('System Administrator', 'admin@kitapkuurdu.com', '123456', 'admin'),
    ('Can Yýlmaz', 'deneme@mail.com', 'test1234', 'customer'),
    ('Elif Kaya', 'elif.kaya@mail.com', 'elifpass', 'customer'),
    ('Burak Öztürk', 'burak.ozturk@mail.com', 'burakpass', 'customer');

    PRINT '>>> Users inserted.';
END
GO

-- =============================================
-- 3. INSERT BOOKS
-- =============================================
IF NOT EXISTS (SELECT 1 FROM Books)
BEGIN
    INSERT INTO Books (BookName, CategoryID, Author, Price, ImageUrl, Stock) VALUES 
    
    -- CHILDREN (ID: 4)
    ('Anne Terliði', 4, 'Anýl Basýlý', 100.00, 'books/anne-terligi-9786256581944.jpg', 156),
    ('Kýnalý Serçe', 4, 'Ýlber Ortaylý', 100.00, 'books/Kýnalý-Serçe.jpg', 98),
    ('Ayvayý Yedik Müzesi', 4, 'Mert Arýk', 80.67, 'books/ayvayý-yedik.jpg', 70),
    ('Yýldýzlara Yakýn', 4, 'Metin Özdamar', 70.50, 'books/yýldýzlara-yakýn.jpg', 140),
    ('Çantamdan Fil Çýktý', 4, 'Mert Arýk', 75.50, 'books/çantamdan-fil-çýktý.jpg', 70),
    ('Uzaya Giden Tren', 4, 'Mert Arýk', 80.50, 'books/uzaya-giden-tren.jpg', 65),

    -- NOVEL (ID: 1)
    ('Kürk Mantolu Madonna', 1, 'Sabahattin Ali', 100.00, 'books/kürk-mantolu-madonna.jpg', 80),
    ('Dönüþüm', 1, 'Franz Kafka', 35.50, 'books/dönüþüm.jpg', 110),
    ('Bekle Beni', 1, 'Zülfü Livaneli', 180.00, 'books/bekle-beni.jpg', 280),
    ('Bahçývan ve Ölüm', 1, 'Georgi Gospodinov', 299.78, 'books/bahçývan-ve-ölüm.jpg', 134),
    ('Gece Yarýsý Kütüphanesi', 1, 'Matt Haig', 190.78, 'books/gece-yarýsý-kütüphanesi.jpg', 174),
    ('Kardeþimin Hikayesi', 1, 'Livaneli', 149.90, 'books/kardeþimin-hikayesi.jpg', 94),
    ('Uðultulu Tepeler', 1, 'Emily Bronte', 199.78, 'books/uðultulu-tepeler.jpg', 54),
    ('Otomatik Portakal', 1, 'Anthony Burgess', 89.98, 'books/otomatik-portakal.jpg', 74),
    ('Doðu Ekspresindeki Cinayet', 1, 'Agatha Christie', 149.88, 'books/doðu-ekspresi.jpg', 260),
    ('Veronika Ölmek Ýstiyor', 1, 'Paulo Coelho', 179.78, 'books/veronik-ölmek-istiyor.jpg', 284),
    ('Sefiller -Set', 1, 'Victor Hugo', 329.78, 'books/sefiller.jpg', 283),
    ('Simyacý', 1, 'Paulo Coelho', 174.78, 'books/simyacý.jpg', 334),
    ('Ýlahi Komedya -Cehennem', 1, 'Dante Alighieri', 139.78, 'books/cehennem.jpg', 294),
    ('Ýlahi Komedya -Araf', 1, 'Dante Alighieri', 119.78, 'books/araf.jpg', 244),
    ('Ýlahi Komedya -Cennet', 1, 'Dante Alighieri', 129.78, 'books/cennet.jpg', 194),
    ('Aþk ve Gurur', 1, 'Jane Austen', 192.50, 'books/aþk-ve-gurur.jpg', 221),

    -- PHILOSOPHY (ID: 2)
    ('Devlet', 2, 'Platon', 85.00, 'books/devlet.jpg', 130),
    ('Sokrates in Savunmasý', 2, 'Platon', 85.00, 'books/sokratesin-savunmasý.jpg', 213),
    ('Nikomakhos a Etik', 2, 'Aristoteles', 199.70, 'books/nikomakhosa-etik.jpg', 60),
    ('Meditasyon', 2, 'Marcus Aurelius', 120.00, 'books/meditasyon.jpg', 112),
    ('Varoluþçuluk', 2, 'Jean-Paul Sartre', 99.40, 'books/varoluþçuluk.jpg', 192),
    ('Utopia', 2, 'Thomas More', 83.20, 'books/utopia.jpg', 73),
    ('Duygusal Zeka', 2, 'Daniel Goleman', 85.00, 'books/duygusal-zeka.jpg', 179),

    -- SELF IMPROVEMENT (ID: 5)
    ('Sevebilmek', 5, 'Guy Finley', 174.67, 'books/4145axlI8eL._AC_UY327_FMwebp_QL65_.jpg', 167),
    ('Modern Ruhu Kurtarmak', 5, 'Eva Illouz', 269.45, 'books/modern-ruhu-kurtarmak.jpg', 145),
    ('Vizyon ve Misyon', 5, 'Metin Kan', 80.33, 'books/vizyon-misyon.jpg', 69),
    ('Bilinçaltý Çalýþmasý', 5, 'Joseph Murphy', 197.67, 'books/bilinçaltý-çalýþmasý.jpg', 126),
    ('50 Kiþisel Geliþim Klasiði', 5, 'Tom Butler-Bowdon', 188.45, 'books/50-kiþisel-geliþim.jpg', 345),
    ('Kiþisel Geliþim Çýlgýnlýðýnda Kendiniz Kalabilmek', 5, 'Svend Brinkmann', 146.79, 'books/kiþisel-geliþim-çýlgýnlýðý.jpg', 165),
    ('Atomik Alýþkanlýklar', 5, 'James Clear', 134.45, 'books/atomik-alýþkanlýklar.jpg', 167),
    ('Ustalýk Gerektiren Kafaya Takmama Sanatý', 5, 'Mark Manson', 159.45, 'books/kafaya-takmama-sanatý.jpg', 276),
    ('Hayýr Diyebilme Sanatý', 5, 'Müthiþ Psikoloji', 123.78, 'books/müthiþ-psikoloji.jpg', 114),
    ('Ýyi Hissetmek', 5, 'David D. Burns', 299.12, 'books/iyi-hissetmek.jpg', 209),
    ('Ýnsanýn Anlam Arayýþý', 5, 'Viktor Frankl', 125.67, 'books/insanýn-anlam-arayýþý.jpg', 123),
    ('Düþün Ve Zengin Ol', 5, 'Napoleon Hill', 184.34, 'books/düþün-ve-zengin-ol.jpg', 281),
    ('Olumlu Düþüncenin Gücü', 5, 'Norman Vincent Peale', 167.43, 'books/olumlu-düþüncenin-gücü.jpg', 247),
    ('Asla Yalnýz Yeme', 5, 'Keith Ferrazzi', 169.99, 'books/asla-yalnýz-yeme.jpg', 250),
    ('Beþinci Disiplin', 5, 'Peter M. Senge', 99.90, 'books/beþinci-disiplin.jpg', 98),

    -- COMICS & MANGA (ID: 3)
    ('Batman - Yeni Dünya', 3, 'Geoff Johns', 262.45, 'books/batman-yeni-dünya.jpg', 110),
    ('Berserk Cilt 1', 3, 'Kentaro Miura', 150.56, 'books/berserk.jpg', 291),
    ('Berserk Cilt 2', 3, 'Kentaro Miura', 140.16, 'books/berserk2.jpg', 101),
    ('Berserk Cilt 3', 3, 'Kentaro Miura', 120.56, 'books/berserk3.jpg', 163),
    ('Berserk 1-8 Ciltleri', 3, 'Kentaro Miura', 2193.56, 'books/berserk8.jpg', 71),
    ('Hikarunun Veda Ettiði Yaz Cilt 1', 3, 'Mokumokuren', 123.45, 'books/hikaru1.jpg', 165),
    ('Hikarunun Veda Ettiði Yaz Cilt 2', 3, 'Mokumokuren', 120.45, 'books/hikaru2.jpg', 115),
    ('Hikarunun Veda Ettiði Yaz Cilt 3', 3, 'Mokumokuren', 133.56, 'books/hikaru3.jpg', 145),
    ('Hikarunun Veda Ettiði Yaz Cilt 4', 3, 'Mokumokuren', 103.25, 'books/hikaru4.jpg', 95),
    ('Kýzýl Ýblisin Dönüþü 1', 3, 'Azi-Wolbaek', 50.45, 'books/kýzýl1.jpg', 139),
    ('Kýzýl Ýblisin Dönüþü 2', 3, 'Azi-Wolbaek', 45.45, 'books/kýzýl2.jpg', 99),
    ('Kýzýl Ýblisin Dönüþü 3', 3, 'Azi-Wolbaek', 56.45, 'books/kýzýl3.jpg', 100);

    PRINT '>>> Book data inserted successfully.';
END
GO