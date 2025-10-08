from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, func, Boolean, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url_pattern = Column(String, nullable=False, unique=True)
    trust_score = Column(Integer, default=5)

    posts = relationship("Post", back_populates="source")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    post_id = Column(String, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    credibility_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)  # <-- Add this
    source_id = Column(Integer, ForeignKey("sources.id"))
    advanced_score = Column(Float, nullable=True)
    score_explanation = Column(JSON, nullable=True)
    community_sentiment = Column(Float, nullable=True)
    verified_manual = Column(Boolean, default=False) 

    source = relationship("Source", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String, nullable=False, unique=True)
    text = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))
    sentiment_score = Column(Float, nullable=True)  # <-- Add this
    is_sarcastic = Column(Boolean, default=False)
    language = Column(String, nullable=True)

    post = relationship("Post", back_populates="comments")

