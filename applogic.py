from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base , All_cat ,All_item

engine=create_engine('sqlite:///catelog.db')

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind = engine)
session = DBSession()
#setup data in Category mobile
mobile = All_cat(name = "Mobile")
session.add(mobile)
session.commit()
#_____Start Setup data in category/item/mobile__________
phone = All_item(name = "Samsung",description = "An Android pheone that is more common", category = mobile)
session.add(phone)
session.commit()

phone = All_item(name = "lg k750",description = "An Android phone that is more common and made by Lg company", category = mobile)
session.add(phone)
session.commit()

phone = All_item(name = "Iphone xr ",description = "An ios pheone that is more common and made by Apple company", category = mobile)
session.add(phone)
session.commit()

phone = All_item(name = "Xiomai mi 9",description = "An Android pheone that is more common and made by Xiomai company", category = mobile)
session.add(phone)
session.commit()
#________End_____________


# setup data in Category tv
tv = All_cat(name = "TV")
session.add(tv)
session.commit()
#____start setup data_category/ item/tv_______
telv = All_item(name = "Samsung QLED TV" , description ="Samsung's QLED TVs feature a photo-and-light image over the years" , category = tv)
session.add(telv)
session.commit()

telv = All_item(name = "LG QLED TV" , description ="LG's QLED TVs feature a photo-and-light image over the years made by Lg company" , category = tv)
session.add(telv)
session.commit()

telv = All_item(name = "Apple QLED TV" , description ="Apple's QLED TVs feature a photo-and-light image over the years made by Apple company" , category = tv)
session.add(telv)
session.commit()

telv = All_item(name = "ATA QLED TV" , description ="ATA's QLED TVs feature a photo-and-light image over the years made by ATA company" , category = tv)
session.add(telv)
session.commit()
#_______End______

#start setup data in ctegory laptop
laptop = All_cat(name = "laptop")
session.add(laptop)
session.commit()
#start setup data in category/item /laptopa

lap_top = All_item(name = "Mac" , description = "Production of Apple Mac OS" , category = laptop)
session.add(lap_top)
session.commit()

lap_top = All_item(name = "Dell" , description = "Production of windows or linux made by Dell company" , category = laptop)
session.add(lap_top)
session.commit()

lap_top = All_item(name = "HP" , description = "Production of windows or linux made by Hp company" , category = laptop)
session.add(lap_top)
session.commit()

lap_top = All_item(name = "asus" , description = "Production of  windows or linux made by asus company" , category = laptop)
session.add(lap_top)
session.commit()
print 'Done!'