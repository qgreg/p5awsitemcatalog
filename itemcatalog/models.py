import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
   
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    picture = Column(String(250))
    dateCreated = Column(Date)
    id = Column(Integer, primary_key=True)


class Item(Base):
    __tablename__ = 'item'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    dateCreated = Column(Date)
    description = Column(String(250))
    amazon_href = Column(String(250))
    amazon_src = Column(String(250))
    amazon_img = Column(String(250))
    picture = Column(String(250))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category) 


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    email = Column(String(250))
    picture = Column(String(250))
    admin = Column(Boolean)


engine = create_engine('postgres://ryztryqknsyzog:fVxpW9KcpmHAFAqMo1mBcidICf@ec2-107-21-219-109.compute-1.amazonaws.com:5432/d4kcqmr928j0p2')
Base.metadata.create_all(engine)
