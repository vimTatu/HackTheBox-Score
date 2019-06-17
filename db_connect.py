from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from terminaltables import AsciiTable


Base = declarative_base()


# This object will be used as table markup.
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
        last=str(player.last),
        prev=str(player.prev),
    )
    if not player_exist_in_table(new_scores):
        session.add(new_scores)
        session.commit()
        return True
    last = player_score_changed(new_scores)
    if last:
        return last
    else:
        return False


def player_exist_in_table(score):
    if session.query(Scores).filter(Scores.name == score.name).count() == 0:
        return False
    else:
        return True


def get_players_stats():
    table = [["Nickname", "Score", "Owned Users", "Owned Roots", "Rank"]]
    stats = session.query(Scores).all()
    for user in stats:
        table.append(
            [user.name, user.score, user.users, user.roots, user.rank]
        )
    table = AsciiTable(table)
    return table


def player_score_changed(score):
    record = session.query(Scores).filter(Scores.name == score.name)
    if record.value("last") != score.last:
        session.query(Scores).filter_by(name=score.name).update(
            {
                "score": score.score,
                "roots": score.roots,
                "users": score.users,
                "prev": score.prev,
                "last": score.last,
                "rank": score.rank
            }
        )
        # record.update(score)
        return score.last
    else:
        return False


engine = create_engine("sqlite:///htb.db")
if not os.path.exists("htb.db"):
    Base.metadata.tables["score"].create(bind=engine)

Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()
