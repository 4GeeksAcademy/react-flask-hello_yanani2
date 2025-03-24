from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()


class NoteTag(db.Model):
   
    __tablename__ = 'note_tags'

  
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

  
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

   
    note = db.relationship("Note", back_populates="note_tags")
    tag = db.relationship("Tag", back_populates="note_tags")

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
   
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

   

    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")

   
    def __init__(self, email, password):
        self.email = email
    
        self.set_password(password)
        self.is_active = True

   
    def set_password(self, password):
        self.password = generate_password_hash(password)

   
    def check_password(self, password):
        return check_password_hash(self.password, password)

    
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            
        }

class Note(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
  
    created_at: Mapped[datetime.datetime] = mapped_column(db.DateTime, default=datetime.datetime.utcnow)
  
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)

   
   
    user = relationship("User", back_populates="notes")

   
    note_tags = relationship("NoteTag", back_populates="note", cascade="all, delete-orphan")

  
    tags = relationship("Tag", secondary="note_tags", viewonly=True, overlaps="note_tags, tag")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
            
            "tags": [tag.serialize() for tag in self.tags]
        }

class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

   
    note_tags = relationship("NoteTag", back_populates="tag", cascade="all, delete-orphan")

  
    notes = relationship("Note", secondary="note_tags", viewonly=True, overlaps="note_tags, note")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }