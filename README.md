# 🎮 NextGame Öneri Motoru

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bu proje, kullanıcının girdiği bir oyuna dayanarak anlamsal benzerlik ve yapay zeka kürasyonu kullanarak kişiselleştirilmiş oyun önerileri sunan bir web uygulamasıdır.

## ✨ Özellikler

* **Akıllı Arama:** Siz yazarken oyun isimlerini otomatik tamamlar ve veritabanında var olan oyunları önerir.
* **Anlamsal Öneri:** Girdiğiniz oyuna en çok benzeyen oyunları, oyun açıklamaları ve meta verileri üzerinden hesaplanan vektör benzerlikleri (Sentence Transformers) ile bulur.
* **Yapay Zeka Kürasyonu:** Benzer oyun listesini Google Gemini 2.5 Flash modeline göndererek, aralarından en dikkat çekici 3 tanesini seçer ve her biri için özgün yorumlar (neden önerildiği, kime hitap ettiği) üretir.
* **Çoklu Dil Desteği:** Arayüz metinleri ve LLM tarafından üretilen öneri yorumları için Türkçe ve İngilizce dil seçeneği sunar.
* **Modern Arayüz:** Basit, temiz ve karanlık mod temalı bir web arayüzü.

## 🛠️ Kullanılan Teknolojiler

* **Backend:**
    * Python 3.9+
    * FastAPI (Asenkron web framework)
    * Uvicorn (ASGI sunucusu)
    * SQLAlchemy (ORM - Veritabanı etkileşimi için)
    * SQLite (Geliştirme veritabanı)
    * Sentence Transformers (`all-MiniLM-L6-v2`) (Metin embeddingleri için)
    * Scikit-learn (Kosinüs benzerliği hesaplama için)
    * Google Generative AI SDK (`google-genai`) (Gemini API etkileşimi için)
    * Pandas & PyArrow (Veri işleme ve Parquet okuma için)
    * NumPy (Vektör işlemleri için)
    * python-dotenv (API anahtarı yönetimi için)
* **Frontend:**
    * HTML5
    * CSS3
    * Vanilla JavaScript (API istekleri ve DOM manipülasyonu için)
* **Veri:**
    * İşlenmiş ve birleştirilmiş Steam oyun veri setleri (Kaggle'dan alınmıştır).
    * Oyun meta verileri ve embedding vektörleri SQLite veritabanında saklanır.

## 🏗️ Mimari Akışı (Basit)

1.  **Kullanıcı Girişi:** Frontend'den oyun adı araması başlar.
2.  **Arama API (`/search/`):** FastAPI, isteği alır ve `crud.py`'deki fonksiyonu çağırır.
3.  **Veritabanı (Arama):** `crud.py`, SQLite veritabanından eşleşen oyun adlarını ve logolarını çeker.
4.  **Frontend (Arama Sonuçları):** Sonuçlar frontend'e döner ve otomatik tamamlama listesi gösterilir.
5.  **Kullanıcı Seçimi:** Kullanıcı bir oyun seçer ve "Öneri Getir" butonuna basar.
6.  **Öneri API (`/recommend/`):** FastAPI, isteği (oyun adı ve dil ile) alır.
7.  **Veritabanı (Benzerlik):** `crud.py`, hedef oyunun vektörünü ve diğer tüm oyunların vektörlerini çeker, kosinüs benzerliğini hesaplar ve en benzer 20 oyunun `text_for_embedding` verisini döndürür.
8.  **LLM Servisi (`llm_responses.py`):** Backend, bu 20 metni ve seçilen dili Google Gemini 2.5 Flash modeline gönderir.
9.  **Yapay Zeka Analizi:** Gemini, metinleri analiz eder, 3 oyun seçer ve JSON formatında yorumları (gerekçe, not) oluşturur.
10. **Frontend (Öneriler):** Sonuçlar frontend'e döner ve öneri kartları gösterilir.

## 📸 Ekran Görüntüleri

\[Buraya çalışan uygulamanın birkaç ekran görüntüsünü veya kısa bir GIF'ini ekleyin. Arama kutusu, öneri sonuçları vb.]

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

1.  **Depoyu Klonlayın:**
    ```bash
    git clone [https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git](https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git)
    cd PROJE_ADINIZ
    ```

2.  **Sanal Ortam Oluşturun ve Aktive Edin:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Gereksinimleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **API Anahtarını Ayarlayın:**
    * Projenin ana dizininde `.env` adında bir dosya oluşturun.
    * İçine Google AI Studio'dan aldığınız API anahtarını ekleyin:
        ```env
        GEMINI_API_KEY=BURAYA_API_ANAHTARINIZI_YAPISTIRIN
        ```

5.  **Veritabanını Hazırlayın:**
    * \[**SEÇENEK 1 (Önerilen):** Eğer `nextgame.db` dosyasını depoya eklediyseniz, bu adımı atlayabilirsiniz.]
    * \[**SEÇENEK 2:** Gerekli Parquet dosyasını (`data_with_embeddings.parquet`) projenin ana dizinine yerleştirin.]
    * Aşağıdaki komutla veritabanını oluşturun ve verileri yükleyin (Bu işlem biraz zaman alabilir):
        ```bash
        python populate_db.py 
        ```
        *(Not: `populate_db.py` script'inin doğru Parquet dosya yolunu kullandığından emin olun.)*

6.  **Sunucuyu Başlatın:**
    ```bash
    uvicorn main:app --reload --port 8000 
    ```
    *(Veya farklı bir port kullanmak isterseniz `--port PORT_NUMARASI` ekleyin.)*

7.  **Uygulamayı Açın:**
    Tarayıcınızda `http://127.0.0.1:8000` (veya belirlediğiniz port) adresine gidin.

## 📝 API Endpoints (Kısaca)

* `GET /`: Frontend `index.html` dosyasını sunar.
* `GET /search/?q={query}`: Girilen `query` ile başlayan oyun adlarını ve logolarını döndürür (otomatik tamamlama için).
* `GET /recommend/?game_name={name}&lang={tr|en}`: Belirtilen `game_name` için `lang` dilinde (varsayılan 'en') 3 oyun önerisi döndürür.

## 🌱 Gelecek İyileştirmeler (Fikirler)

* Kullanıcı hesapları ve Steam entegrasyonu (`User` modeli).
* Kullanıcının sahip olduğu oyunlara göre kişiselleştirilmiş öneriler.
* PostgreSQL ve `pgvector` eklentisi ile daha verimli vektör araması.
* Daha gelişmiş filtreleme seçenekleri (tür, etiket, fiyat aralığı vb.).
* İşbirlikçi filtreleme (Collaborative Filtering) yöntemlerinin eklenmesi.
* Frontend'i Next.js gibi modern bir framework ile yeniden yazmak.

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız. \[Eğer bir LICENSE dosyası eklemediyseniz, GitHub üzerinden kolayca ekleyebilirsiniz.]

---

Umarım bu README taslağı işini görür! Başka eklemek veya değiştirmek istediğin bir şey olursa söylemen yeterli.