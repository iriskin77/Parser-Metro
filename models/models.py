import sqlalchemy as db
from sqlalchemy import orm, sql
from typing import TypeAlias
from datetime import datetime

Base: TypeAlias = orm.declarative_base()  # type: ignore



class Good(Base):

    __tablename__ = 'Goods'

    good_id: int = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    name: str = db.Column(db.String(255), nullable=False)
    new_price: int = db.Column(db.Integer, nullable=True)
    old_price: int = db.Column(db.Integer, nullable=False)
    brand_id: int = db.Column(db.Integer, db.ForeignKey('Brands.brand_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    link: str = db.Column(db.String(10000), nullable=False)

class Brand(Base):

    __tablename__ = 'Brands'

    brand_id: int = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    good_id: int = db.Column(db.Integer, db.ForeignKey(Good.good_id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    name: str = db.Column(db.String(255), nullable=False)




class Category(Base):

    __tablename__ = 'Category'

    category_id: int = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    good_id: int = db.Column(db.Integer, db.ForeignKey(Good.good_id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    name: str = db.Column(db.String(255), nullable=False)


engine = db.create_engine('sqlite:///myDatabase.db')





