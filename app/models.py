from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# ---- Sources ----
class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url_pattern = Column(String(200), unique=True, nullable=False)  # e.g. "bbc.com"
    trust_score = Column(Integer, default=5)  # scale: 0-10

    posts = relationship("Post", back_populates="source")


# ---- Posts ----
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # Reddit, Twitter
    post_id = Column(String(100), unique=True, nullable=False)  # external ID from API
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    credibility_score = Column(Float, default=0.0)  # combined score
    sentiment_score = Column(Float, default=0.0)    # overall sentiment

    source_id = Column(Integer, ForeignKey("sources.id"))
    source = relationship("Source", back_populates="posts")

    comments = relationship("Comment", back_populates="post")


# ---- Comments ----
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String(100), unique=True, nullable=False)  # external ID
    text = Column(Text, nullable=False)
    sentiment = Column(Float, default=0.0)  # sentiment score
    stance = Column(String(20), default="neutral")  # support / deny / neutral

    post_id = Column(Integer, ForeignKey("posts.id"))
    post = relationship("Post", back_populates="comments")
