import pandas as pd

df_final_cleaned = pd.read_parquet("C:/Projects/game/dataset.parquet")

# 1. Farklı formatlardaki tarih metinlerini standart bir tarih objesine çevir
# Tanınamayanları NaT (boş tarih) olarak işaretle
df_final_cleaned['release_date'] = pd.to_datetime(df_final_cleaned['release_date'], errors='coerce')

# 2. Sonucu kontrol edelim
# Dtype'ın 'datetime64[ns]' olduğuna dikkat et
print("--- Dönüşüm Sonrası Bilgi ---")

# 3. Dönüşemeyen (NaT olan) satırlar var mı diye bakalım
invalid_dates = df_final_cleaned[df_final_cleaned['release_date'].isnull()]
if not invalid_dates.empty:
    print(f"\n{len(invalid_dates)} adet tarih dönüştürülemedi ve NaT olarak işaretlendi.")
    # Bu NaT değerlerini ne yapacağımıza karar verebiliriz. Örneğin en eski tarihle doldurabiliriz.
    earliest_date = df_final_cleaned['release_date'].min()
    df_final_cleaned['release_date'].fillna(earliest_date, inplace=True)
    print("Dönüşemeyen tarihler, en eski tarih ile dolduruldu.")


# 4. Veritabanına kaydetmek için tarihi tekrar 'YYYY-MM-DD' formatında metne çevirelim
# .dt erişimcisi, tarih işlemleri yapmamızı sağlar
df_final_cleaned['release_date'] = df_final_cleaned['release_date'].dt.strftime('%Y-%m-%d')

print("\n--- Son Hali (Örnek) ---")
print(df_final_cleaned['release_date'].head())

# 5. Sonucu tekrar parquet olarak kaydedelim
df_final_cleaned.to_parquet("C:/Projects/game/dataset_cleaned.parquet", index=False)