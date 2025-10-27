from sqlalchemy import Column, Integer, String, Float, Text, BLOB, Date, Boolean
from sqlalchemy_utils import URLType
from database.db import Base

class Game(Base):
    __tablename__ = "games"

    appid = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    release_date = Column(Date)
    required_age = Column(Integer)
    price = Column(Float)
    dlc_count = Column(Integer, nullable=True)

    header_image = Column(URLType, nullable=True)
    website = Column(URLType, nullable=True)

    windows = Column(Boolean, nullable=True)
    mac = Column(Boolean, nullable=True)
    linux = Column(Boolean, nullable=True)

    supported_languages = Column(Text, nullable=True)
    genres = Column(Text)
    tags = Column(Text)
    categories = Column(Text)

    
    developers = Column(Text)
    publishers = Column(Text)


    text_for_embedding = Column(Text, nullable=False)
    embedding = Column(BLOB, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    steamid = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    game_count = Column(Integer, default=0)
    game_info = Column(Text, nullable=True)  # JSON formatında oyun bilgisi
    is_superuser = Column(Boolean, default=False)

    ".... To be continued ...."