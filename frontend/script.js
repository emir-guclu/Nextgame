// --- DİL ÇEVİRİ METİNLERİ ---
const translations = {
    "tr": {
        "page_title": "NextGame Öneri Motoru",
        "main_title": "🎮 NextGame Öneri Motoru",
        "subtitle": "Sevdiğin bir oyunu yaz, sana benzerlerini ve yeni cevherleri bulalım.",
        "placeholder_text": "Örn: The Witcher 3: Wild Hunt",
        "button_text": "Öneri Getir",
        "language_label": "Öneri Dili:",
        "loading_text": "Analiz ediliyor, lütfen bekleyin...",
        "error_no_game": "Lütfen bir oyun adı girin.",
        "error_search_fail": "Arama başarısız oldu.",
        "error_recommend_fail": "Sunucu hatası:",
        "recommend_not_found": "Bu oyuna uygun bir öneri bulunamadı.",
        "card_type_similar": "Bu Oyuna Çok Benzer",
        "card_type_alternative": "Alternatif Cevher",
        "card_type_noteworthy": "Dikkate Değer",
        "card_reason_label": "Neden Önerildi?",
        "card_note_label": "Not:"
    },
    "en": {
        "page_title": "NextGame Recommendation Engine",
        "main_title": "🎮 NextGame Recommendation Engine",
        "subtitle": "Enter a game you love, and we'll find similar ones and hidden gems.",
        "placeholder_text": "E.g.: The Witcher 3: Wild Hunt",
        "button_text": "Get Recommendations",
        "language_label": "Recommendation Language:",
        "loading_text": "Analyzing, please wait...",
        "error_no_game": "Please enter a game name.",
        "error_search_fail": "Search failed.",
        "error_recommend_fail": "Server error:",
        "recommend_not_found": "No suitable recommendations found for this game.",
        "card_type_similar": "Very Similar to This Game",
        "card_type_alternative": "Alternative Gem",
        "card_type_noteworthy": "Noteworthy",
        "card_reason_label": "Why Recommended?",
        "card_note_label": "Note:"
    }
};

// --- ARAYÜZ METİNLERİNİ GÜNCELLEME FONKSİYONU ---
function updateUIText(lang) {
    // Sayfanın genel dilini ayarla
    document.getElementById('htmlLang').lang = lang;
    // Sayfa başlığını güncelle
    document.getElementById('pageTitle').textContent = translations[lang]['page_title'];

    // data-translate attribute'u olan tüm elementleri bul ve çevir
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            // Placeholder için özel durum
            if (key === 'placeholder_text' && element.tagName === 'INPUT') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });
}


// --- DEBOUNCE FONKSİYONU ---
// Kullanıcı yazmayı bıraktığında arama yapmak için
let debounceTimer;
function debounce(func, delay) {
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    }
}

// --- GLOBAL DEĞİŞKEN ---
// Seçili olan dil kodunu tutmak için (tr: Türkçe, en: İngilizce)
let currentLanguage = 'tr'; // Varsayılan olarak Türkçe başlasın

// Sayfa tamamen yüklendiğinde çalışacak ana fonksiyon
document.addEventListener('DOMContentLoaded', () => {

    // HTML'den gerekli elementleri seç ve değişkenlere ata
    const searchButton = document.getElementById('searchButton');
    const gameInput = document.getElementById('gameInput');
    const searchResultsBox = document.getElementById('search-results-box');
    const langButtons = document.querySelectorAll('.lang-button'); // Tüm dil butonlarını seç

    // --- OLAY DİNLEYİCİLERİ (EVENT LISTENERS) ---

    // "Öneri Getir" butonuna tıklanınca getRecommendations fonksiyonunu çağır
    searchButton.addEventListener('click', getRecommendations);

    // Arama kutusundayken Enter tuşuna basılınca getRecommendations fonksiyonunu çağır
    gameInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            getRecommendations();
        }
    });

    // Arama kutusuna her harf girildiğinde (300ms gecikmeyle) handleSearchInput fonksiyonunu çağır
    gameInput.addEventListener('input', debounce(handleSearchInput, 300));

    // Sayfanın herhangi bir yerine (arama kutusu/listesi dışına) tıklandığında arama sonuçlarını gizle
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.search-container')) {
            searchResultsBox.style.display = 'none';
        }
    });

    // Dil seçici butonlara tıklanınca çalışacak kod
    langButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Önce tüm butonlardan 'active' stilini kaldır
            langButtons.forEach(btn => btn.classList.remove('active'));
            // Sadece tıklanan butona 'active' stilini ekle
            button.classList.add('active');
            // Seçili dili butonun 'data-lang' özelliğinden al ve global değişkene ata
            currentLanguage = button.getAttribute('data-lang');
            console.log("Dil değiştirildi:", currentLanguage); // Tarayıcı konsoluna bilgi yaz
            updateUIText(currentLanguage); // ARAYÜZ METNİNİ GÜNCELLE
        });
    });

    // --- SAYFA İLK YÜKLENDİĞİNDE ---
    updateUIText(currentLanguage); // Varsayılan dil için metinleri ayarla

}); // DOMContentLoaded bitti


/**
 * Kullanıcı arama kutusuna yazdıkça backend'deki /search/ endpoint'ine istek atar.
 */
async function handleSearchInput() {
    const query = document.getElementById('gameInput').value;
    const searchResultsBox = document.getElementById('search-results-box');

    // Arama yapmak için en az 2 karakter girilmiş olmalı
    if (query.length < 2) {
        searchResultsBox.style.display = 'none'; // Sonuç kutusunu gizle
        return; // Fonksiyondan çık
    }

    try {
        // Backend'e arama isteği gönder (/search/?q=...)
        const response = await fetch(`/search/?q=${encodeURIComponent(query)}`);
        // Eğer sunucudan hata dönerse (örneğin 404), hata fırlat
        if (!response.ok) throw new Error(translations[currentLanguage]['error_search_fail']);

        // Sunucudan gelen JSON yanıtını al
        const data = await response.json();

        // Gelen arama sonuçlarını (oyun listesini) göster
        showSearchResults(data.game_list); // Backend'in 'game_list' anahtarını kullandığını varsayıyoruz

    } catch (error) {
        console.error("Arama Sırasında Hata:", error); // Hatayı konsola yaz
        searchResultsBox.style.display = 'none'; // Hata durumunda sonuç kutusunu gizle
    }
}

/**
 * /search/ endpoint'inden gelen arama sonuçlarını açılır kutuda gösterir.
 * @param {object[]} searchResults - {'name': string, 'header_image': string} objelerini içeren liste
 */
function showSearchResults(searchResults) {
    const gameInput = document.getElementById('gameInput');
    const searchResultsBox = document.getElementById('search-results-box');
    searchResultsBox.innerHTML = ''; // Önceki sonuçları temizle

    if (!searchResults || searchResults.length === 0) {
        searchResultsBox.style.display = 'none'; // Sonuç yoksa kutuyu gizle
        return;
    }

    // Yedek görsel SVG'si (header_image boş veya bozuksa kullanılır)
    const placeholderSVG = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSIzNCIgdmlld0JveD0iMCAwIDYwIDM0Ij48cmVjdCBmaWxsPSIjMzMzMzMzIiB3aWR0aD0iNjAiIGhlaWdodD0iMzQiLz48L3N2Zz4=";

    // Her bir arama sonucu için bir liste öğesi ('div') oluştur
    searchResults.forEach(game => {
        const item = document.createElement('div');
        item.className = 'search-result-item'; // CSS stilini uygula

        // Resim kaynağını belirle: ya oyunun resmi ya da yedek SVG
        const imgSrc = (game.header_image && game.header_image.trim() !== '') ? game.header_image : placeholderSVG;

        // Liste öğesinin içeriğini oluştur (resim + oyun adı)
        item.innerHTML = `
            <img
                src="${imgSrc}"
                alt="${game.name}"
                class="search-result-image"
                onerror="this.onerror=null; this.src='${placeholderSVG}';"
            >
            <span>${game.name}</span>
        `;

        // Bir arama sonucuna tıklandığında:
        item.addEventListener('click', () => {
            gameInput.value = game.name; // Arama kutusunu tıklanan oyunun adıyla doldur
            searchResultsBox.style.display = 'none'; // Sonuç kutusunu gizle
        });

        // Oluşturulan öğeyi sonuç kutusuna ekle
        searchResultsBox.appendChild(item);
    });

    searchResultsBox.style.display = 'block'; // Sonuç kutusunu görünür yap
}


/**
 * "Öneri Getir" butonuna basıldığında backend'deki /recommend/ endpoint'ine istek atar.
 */
async function getRecommendations() {
    const gameName = document.getElementById('gameInput').value; // Arama kutusundaki oyun adı
    const resultsDiv = document.getElementById('results'); // Asıl önerilerin gösterileceği alan
    const loadingDiv = document.getElementById('loading'); // Yükleniyor... mesajı
    const errorDiv = document.getElementById('error'); // Hata mesajı alanı
    const searchResultsBox = document.getElementById('search-results-box'); // Arama sonuç kutusu

    searchResultsBox.style.display = 'none'; // Arama sonuçlarını gizle

    // Oyun adı girilmemişse çevrilmiş hata göster ve fonksiyondan çık
    if (!gameName) {
        errorDiv.textContent = translations[currentLanguage]['error_no_game'];
        errorDiv.style.display = 'block';
        return;
    }

    // Önceki sonuçları ve hataları temizle, yükleniyor mesajını göster
    resultsDiv.innerHTML = '';
    errorDiv.style.display = 'none';
    // Yükleniyor mesajını çevir
    loadingDiv.textContent = translations[currentLanguage]['loading_text']; 
    loadingDiv.style.display = 'block';

    try {
        // Seçili olan dili global değişkenden al (butonlardan ayarlanmıştı)
        const preferredLanguage = currentLanguage;

        // Backend API adresini oluştur (örneğin: /recommend/?game_name=The%20Witcher%203&lang=tr)
        const apiUrl = `/recommend/?game_name=${encodeURIComponent(gameName)}&lang=${preferredLanguage}`;

        console.log("Öneri İsteği Gönderiliyor:", apiUrl); // Konsola hangi adrese istek atıldığını yaz

        // Backend'e öneri isteğini gönder
        const response = await fetch(apiUrl);

        // Sunucudan hata dönerse (örneğin 404, 500), hata fırlat
        if (!response.ok) {
            // Hata mesajını JSON olarak okumaya çalış
            const errorData = await response.json().catch(() => ({ detail: `${translations[currentLanguage]['error_recommend_fail']} ${response.statusText}` }));
            // FastAPI'nin 'detail' anahtarını kullan veya genel bir mesaj göster
            throw new Error(errorData.detail || `${translations[currentLanguage]['error_recommend_fail']} ${response.statusText}`);
        }

        // Sunucudan gelen JSON yanıtını al
        const data = await response.json();

        // Gelen önerileri ekrana yazdır
        displayRecommendations(data.recommendations); // Backend'in 'recommendations' anahtarını kullandığını varsayıyoruz

    } catch (error) {
        console.error("Öneri Sırasında Hata:", error); // Hatayı konsola yaz
        // Hata mesajını çevir (Başına "Hata: " ekleyebiliriz)
        errorDiv.textContent = `Hata: ${error.message}`; 
        errorDiv.style.display = 'block';
    } finally {
        // İşlem bitince (başarılı veya hatalı) yükleniyor mesajını gizle
        loadingDiv.style.display = 'none';
    }
}

/**
 * /recommend/ endpoint'inden gelen ASIL önerileri ekranda kartlar halinde gösterir.
 * @param {object[]} recommendations - Önerilen oyunların objelerini içeren liste
 */
function displayRecommendations(recommendations) {
    const resultsDiv = document.getElementById('results');

    // Öneri yoksa veya boşsa çevrilmiş bilgi mesajı göster
    if (!recommendations || recommendations.length === 0) {
        resultsDiv.innerHTML = `<p>${translations[currentLanguage]['recommend_not_found']}</p>`;
        return;
    }

    // Her bir öneri için bir kart ('div') oluştur
    recommendations.forEach((game, index) => {
        const card = document.createElement('div');
        card.className = 'game-card'; // CSS stilini uygula
        // Kartların sırayla belirmesi için küçük bir animasyon gecikmesi
        card.style.animationDelay = `${index * 0.1}s`;

        // Kart türünü çevir
        let cardType = translations[currentLanguage]['card_type_noteworthy']; // Varsayılan
        if (game.type === 'Similar') {
            cardType = translations[currentLanguage]['card_type_similar'];
        } else if (game.type === 'Alternative') {
            cardType = translations[currentLanguage]['card_type_alternative'];
        }

        // Kartın içeriğini oluştur (LLM'den gelen verilere göre ve çevrilmiş etiketlerle)
        card.innerHTML = `
            <h2>${game.game_name}</h2>
            <div class="type">${cardType}</div>
            <p><strong>${translations[currentLanguage]['card_reason_label']}</strong> ${game.match_reason}</p>
            <p><strong>${translations[currentLanguage]['card_note_label']}</strong> ${game.user_note}</p>
        `;
        // Oluşturulan kartı sonuç alanına ekle
        resultsDiv.appendChild(card);
    });
}