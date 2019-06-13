from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


engine = create_engine("sqlite:///htb.db")
if not os.path.exists("ctfs.db"):
    Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()


# This class will be used as table markup.
class Scores(Base):
    __tablename__ = "score"
    name = Column(String(256), primary_key=True)
    score = Column(Integer)
    users = Column(Integer)
    roots = Column(Integer)
    rank = Column(String(128))
    last = Column(String(256))
    prev = Column(String(256))


def add_item(player):
    new_scores = Scores(
        name=player.name,
        score=player.score,
        users=player.users,
        roots=player.roots,
        rank=player.rank,
        last=player.last,
        prev=player.prev,
    )
    if is_unique(new_scores):
        session.add(new_scores)
        session.commit()
        return True
    return False


def is_unique(score):
    return session.query(Scores).filter(Scores.last == score.last).count() == 0
