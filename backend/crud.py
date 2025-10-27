from sqlalchemy.orm import Session
from database.tables import Game # Game modelini import ettiğinden emin ol
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


EMBEDDING_DIM = 384
EMBEDDING_DTYPE = np.float32


def search_games_by_name(db: Session, query: str, limit: int = 10):
    """
    Oyun adlarına göre case-insensitive (büyük/küçük harf duyarsız) 
    'ile başlar' araması yapar.
    """
    
    # arama sorgusunu oluşturuyoruz. 'Witch' -> 'Witch%'
    # '%' karakteri SQL'de "gerisi ne olursa olsun" anlamına gelen bir wildcard'dır.
    search_query = f"{query}%"
    
    # .ilike() komutu, case-insensitive LIKE sorgusu atar.
    # Bu, 'witch' yazsan da 'Witcher'ı bulur.
    search_results = db.query(Game.name, Game.header_image) \
                       .filter(Game.name.ilike(search_query)) \
                       .limit(limit) \
                       .all()
    
    # Sonuçlar [('Oyun Adı 1',), ('Oyun Adı 2',)] şeklinde bir tuple listesi olarak gelir.
    # Bunu ['Oyun Adı 1', 'Oyun Adı 2'] şeklinde temiz bir listeye çevirelim.
    games_list = [
        {"name" : name, "header_image": header_image}
        for (name, header_image) in search_results
    ]
    
    return games_list

def get_similar_game_embeddings_and_texts(db : Session, target_game_name : str, top_n : int = 20) -> list[str]:
    """
        Verilen oyun adına göre veritabanındaki embedding vektörlerini kullanarak
        en benzer 'top_n' adet oyunun 'text_for_embedding' metinlerini döndürür.

        Args:
            db: SQLAlchemy database session.
            target_game_name: Benzerleri bulunacak oyunun adı.
            top_n: Döndürülecek en benzer oyun sayısı.

        Returns:
            En benzer 'top_n' oyunun text_for_embedding metinlerinin listesi.
            Oyun bulunamazsa veya hata olursa boş liste döner.
        """
    
    target_game = db.query(Game.appid, Game.embedding).filter(Game.name == target_game_name).first()

    if not target_game:
        return []
    
    target_appid, target_embedding_blob = target_game

    try:
        target_vector = np.frombuffer(target_embedding_blob, dtype=EMBEDDING_DTYPE).reshape(1, -1)
        if target_vector.shape != (1, EMBEDDING_DIM):
            raise ValueError(f"Beklenmeyen vektör boyutu: {target_vector.shape}")
    except Exception as e:
        print(f"Hata hedef oyun embedding vektörü okunamadı. Appid : {target_appid}, Hata : {e}")
        return []
    
    all_games_data = db.query(Game.appid, Game.embedding).all()

    if not all_games_data:
        print("Hata veri tabanında oyun verisi çekilemedi")
        return []

    all_appids = []
    all_embedding_list = []
    valid_indices = []

    for i, (appid, embedding_blob) in enumerate(all_games_data):
        all_appids.append(appid)

        try:
            vector = np.frombuffer(embedding_blob, dtype=EMBEDDING_DTYPE)

            if vector.shape == (EMBEDDING_DIM,):
                all_embedding_list.append(vector)
                valid_indices.append(i)
            else:
                print(f"Uyarı: AppID {appid} için geçersiz vektör boyutu: {vector.shape}")
        except Exception as e:
            print(f"Uyarı: AppID {appid} için embedding okunamadı. Hata: {e}")
            continue

    if not all_embedding_list:
        print("Hata: Hiç geçerli embedding vektörü bulunamadı.")
        return []
    
    embedding_matrix = np.array(all_embedding_list)

    cosine_scores = cosine_similarity(target_vector, embedding_matrix)[0]

    most_similar_indicies = cosine_scores.argsort()[- (top_n + 1) :][::-1]

    similar_appids_ordered = []

    for index in most_similar_indicies:
        retrieved_appid = all_appids[index] 

        if retrieved_appid != target_appid: 
            similar_appids_ordered.append(retrieved_appid)

        if len(similar_appids_ordered) == top_n:
            break

    if not similar_appids_ordered:
        print("Hiç benzer oyun bulunamadı.")
        return []

    similar_game_texts_unordered = db.query(Game.appid, Game.text_for_embedding).filter(Game.appid.in_(similar_appids_ordered)).all()

    texts_dict = {appid : text for appid, text, in similar_game_texts_unordered}

    ordered_texts = [texts_dict.get(appid, "") for appid in similar_appids_ordered if appid in texts_dict]

    return ordered_texts
