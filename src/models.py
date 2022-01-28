from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, index=True)
    term_id = Column(String, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    request = relationship("Request", back_populates="entries")

class Definition(Base):
    __tablename__ = "definitions"

    id = Column(Integer, primary_key=True, index=True)
    definition = Column(String, index=True)
    lan = Column(String, index=True)
    lemma = Column(String, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    request = relationship("Request", back_populates="definitions")

class Dictionary(Base):
    __tablename__ = "dictionaries"

    id = Column(Integer, primary_key=True, index=True)
    id_dict = Column(String, index=True)
    # endpoint = Column(String, index=True)
    apiKey  = Column(String, index=True)

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("dictionaries.id"))
    target_id = Column(Integer, ForeignKey("dictionaries.id"), default=1)
    file = Column(String, index=True)
    status = Column(String, default="PROCESSING")

    entries = relationship("Entry", back_populates="request")
    definitions = relationship("Definition", back_populates="request")
    source = relationship("Dictionary", foreign_keys=[source_id])
    target = relationship("Dictionary", foreign_keys=[target_id])
