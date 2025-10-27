import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime
from pathlib import Path

from database.db import SessionLocal, engine
from database.tables import Game, User
from database.create_db import create_tables

create_tables()

PARQUET_FILE = Path("C:/Projects/game/dataset_cleaned.parquet")

try:
    df = pd.read_parquet(PARQUET_FILE)
    print(f"Parquet file loaded successfully with {len(df)} records.")
except FileNotFoundError:
    raise FileNotFoundError(f"Parquet file not found at {PARQUET_FILE}. Please ensure the file exists.")
except Exception as e:
    raise RuntimeError(f"An error occurred while reading the Parquet file: {e}")

db = SessionLocal()

print("Populating the database with game data...")

try:
    for _, row in tqdm(df.iterrows(), total=df.shape[0]):

        release_date_obj = None

        try:
            release_date_str = row.get("release_date", '')
            if isinstance(release_date_str, str) and release_date_str:
                for fmt in ("%Y-%m-%d"):
                    try:
                        release_date_obj = datetime.strptime(release_date_str, fmt).date()
                        break
                    except ValueError:
                        continue
        except:
            release_date_obj = None
        
        genres_str = ", ".join(row["genres"]) if isinstance(row["genres"], list) else str(row["genres"])
        tags_str = ", ".join(row["tags"].keys()) if isinstance(row["tags"], dict) else str(row["tags"])
        categories_str = ", ".join(row["categories"]) if isinstance(row["categories"], list) else str(row["categories"])
        supported_languages_str = ", ".join(row["supported_languages"]) if isinstance(row["supported_languages"], list) else str(row["supported_languages"])

        developers = ", ".join(row["developers"]) if isinstance(row["developers"], list) else str(row["developers"])
        publishers = ", ".join(row["publishers"]) if isinstance(row["publishers"], list) else str(row["publishers"])

        embedding_bytes = row["embedding"].tobytes()

        game = Game(
            appid = row["appid"],
            name = row.get("name", ""),
            release_date = release_date_obj,
            required_age = row.get("required_age", 0),
            price = row.get("price", 0.0),
            dlc_count = row.get("dlc_count", 0),

            header_image = row.get("header_image", None),
            website = row.get("website", None),

            windows = row.get("windows", None),
            mac = row.get("mac", None),
            linux = row.get("linux", None),

            supported_languages = supported_languages_str,
            genres = genres_str,
            tags = tags_str,
            categories = categories_str,
            developers = developers,
            publishers = publishers,

            text_for_embedding = row.get("text_for_embedding", ""),
            embedding = embedding_bytes
        )

        db.add(game)

    db.commit()
    print("Database population completed successfully.")

except Exception as e:
    db.rollback()
    raise RuntimeError(f"An error occurred while populating the database: {e}")
finally:
    db.close()
    print("Database session closed.")
