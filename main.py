from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.db import SessionLocal, engine
from backend.crud import search_games_by_name, get_similar_game_embeddings_and_texts
from backend.llm_responses import get_llm_analysis_for_embedding
from database.tables import Base
import uvicorn


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI uygulamasını oluştur
app = FastAPI(
    title="NextGame Recommender API",
    description="Oyun önerileri sunan akıllı bir API.",
    version="0.1.0",
)


# Search Endpoint
@app.get("/search/")
async def search_games(q:str, db: Session = Depends(get_db)):
    """
    Kullanıcı arama çubuğuna yazdıkça otomatik tamamlama önerileri sağlar.
    Kullanım: /search/?q=Witch
    """

    if not q:
        return {"game_list" : []}

    game_list = search_games_by_name(db, query=q, limit=10)
    
    return {"game_list" : game_list}


@app.get("/recommend/")
async def suggestion_games(game_name:str, db : Session = Depends(get_db), lang : Optional[str] = Query("en", enum=["en", "tr"])):
    """
    Verilen oyun adına göre önce benzer oyunları bulur, sonra LLM ile analiz edip
    3 adet (2 benzer, 1 alternatif) öneri döndürür.
    """
    candidate_texts = get_similar_game_embeddings_and_texts(db, target_game_name=game_name, top_n=20)

    if not candidate_texts:
        raise HTTPException(status_code=404, detail=f"'{game_name}' oyunu bulunamadı veya benzerleri hesaplanamadı.")
    
    recommendations = get_llm_analysis_for_embedding(candidate_games=candidate_texts, language=lang) # type: ignore

    if not recommendations:
        raise HTTPException(status_code=500, detail="Öneriler işlenirken bir sunucu hatası oluştu.")
    
    return {"recommendations" : recommendations}




app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)