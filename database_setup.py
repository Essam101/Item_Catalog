from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
	__tablename__ = 'user'
	id = Column(Integer,primary_key =True)
	name = Column(String(100),nullable =False)
	email = Column(String(100),nullable =False)

class All_cat(Base):
	__tablename__ = 'category'

	id = Column(Integer,primary_key = True)
	name = Column(String(60),nullable = False)

	@property
	def serialize(self):
		return {
		'id' : self.id,
		'name' :self.name,

		}
	
	


class All_item(Base):
	__tablename__ = 'items'

	id = Column(Integer,primary_key = True)
	name = Column(String(80),nullable = False)
	description = Column(String(255))
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(All_cat)

	@property
	def serialize(self):
		return {
		'name' :self.name,
		'description': self .description,
		}
	

engine=create_engine('sqlite:///catelog.db')

Base.metadata.create_all(engine)

