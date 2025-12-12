from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TenderStatus(enum.Enum):
    NEW = "NEW"
    INTERESTING = "INTERESTING"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authority = Column(String, nullable=False)  # Auftraggeber
    location = Column(String, nullable=False)
    deadline = Column(String, nullable=False)  # ISO Date - Abgabefrist
    published_at = Column(String, nullable=True)  # Veroeffentlichungsdatum
    budget = Column(String, nullable=True)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TenderStatus), default=TenderStatus.NEW)
    source_url = Column(String, nullable=False)
    source_portal = Column(String, nullable=False)  # Welches Portal
    crawled_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Analysis (optional, wird spaeter gefuellt)
    ai_summary = Column(Text, nullable=True)
    ai_relevance_score = Column(Integer, nullable=True)
    ai_key_risks = Column(Text, nullable=True)  # JSON string
    ai_recommendation = Column(String, nullable=True)


def init_db():
    """Erstellt alle Tabellen in der Datenbank"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency für FastAPI - gibt DB Session zurück"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("Initialisiere Datenbank...")
    init_db()
    print("Datenbank erstellt!")

