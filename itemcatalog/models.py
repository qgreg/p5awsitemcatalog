import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    email = Column(String(250))
    picture = Column(String(250))
    admin = Column(Boolean)


class Category(Base):
    __tablename__ = 'category'
   
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    picture = Column(String(250))
    dateCreated = Column(Date)
    id = Column(Integer, primary_key=True)
    users = relationship(Users)
    users_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'name' : self.name,
            'description' : self.description,
            'dateCreated' : str(self.dateCreated),
            'id' : self.id,
            'picture' : self.picture,
        }


class Item(Base):
    __tablename__ = 'item'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    dateCreated = Column(Date)
    description = Column(String(250))
    amazon_asin = Column(String(250))
    picture = Column(String(250))
    category_id = Column(Integer,ForeignKey('category.id'))
    users_id = Column(Integer, ForeignKey('users.id'))
    category = relationship(Category)
    users = relationship(Users)

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'name' : self.name,
            'description' : self.description,
            'dateCreated' : str(self.dateCreated),
            'id' : self.id,
            'amazon_asin' : self.amazon_asin,
            'picture' : self.picture,
            'category_id' : self.category_id,
        }


engine = create_engine('postgres://ryztryqknsyzog:fVxpW9KcpmHAFAqMo1mBcidICf@ec2-107-21-219-109.compute-1.amazonaws.com:5432/d4kcqmr928j0p2')
Base.metadata.create_all(engine)
