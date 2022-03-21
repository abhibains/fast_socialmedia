from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class Post(Base):  #extends the base class

    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,
                        server_default=text('now()'))
    #using just 'default' wont work
    #using sever_default=TRUE wont work has to be 'TRUE'
    # sql does not modify previously created tables, only creates if absent, so in order to see any changes you need to remove the table.

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    #foreign key has field table_name.column_name
    # action set to CASCADE in case the created of the post is delete from 'users' table
    #datatype of the column must match that of column of the referred table(in this case table: users, column:id)

    owner = relationship("User")
    #referencing the sqlalchemy class and not the table users
    #this will create the relationship of the post with it's creator user


class User(Base):
    #extends base class which is a requirement for any SQLAlchemy model
    __tablename__ = "users"
    email = Column(String, nullable=False, unique=True)
    #will prevent multiple user from having the same email address
    password = Column(String, nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False,
        server_default=text('now()'))  #often times for changes to appear,
    #drop the table in GUI because the code only add table is it isn't present


class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer,
                     ForeignKey("users.id", ondelete="CASCADE"),
                     primary_key=True)
    post_id = Column(Integer,
                     ForeignKey("posts.id", ondelete="CASCADE"),
                     primary_key=True)
