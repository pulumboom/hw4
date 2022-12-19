from sqlalchemy import Enum, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import enum

from sqlalchemy.orm import relationship

Base = declarative_base()


class AttackTypeEnum(enum.Enum):
    Physical = 1
    Magic = 2


class LocationTypeEnum(enum.Enum):
    City = 1
    Underground = 2


class ItemTypeEnum(enum.Enum):
    Weapon = 1
    ChestPlate = 2
    Helmet = 3
    Boots = 4
    Bracers = 5
    Potion = 6
    Pants = 7


class Persons(Base):
    __tablename__ = 'persons'

    user_id = Column(Integer, name='UserID', primary_key=True)
    nickname = Column(String, name='Nickname')
    level = Column(Integer, name='Level')
    hp = Column(Integer, name='HP')
    cur_hp = Column(Integer, name='CurHP')
    money = Column(Integer, name='Money')
    attack = Column(Integer, name='Attack')
    magic_attack = Column(Integer, name='MagicAttack')
    xp = Column(Integer, name='XP')
    armour = Column(Integer, name='Armour')
    magic_armour = Column(Integer, name='MagicArmour')
    weapon = Column(String, default='None')
    helmet = Column(String, default='None')
    chest_plate = Column(String, default='None')
    pants = Column(String, default='None')
    boots = Column(String, default='None')
    bracers = Column(String, default='None')
    location_id = Column(
        Integer,
        ForeignKey('locations.LocationID'),
        name='LocationID'
    )


class Mobs(Base):
    __tablename__ = 'mobs'

    mob_id = Column(Integer, name='MobID', primary_key=True)
    hp = Column(Integer, name='HP')
    xp = Column(Integer, name='XP')
    req_level = Column(Integer, name='ReqLevel')
    attack_type = Column(Enum(AttackTypeEnum), name='AttackType')
    attack = Column(Integer, name='Attack')
    armour = Column(Integer, name='Armour')
    magic_armour = Column(Integer, name='MagicArmour')


class Locations(Base):
    __tablename__ = 'locations'

    location_id = Column(Integer, name='LocationID', primary_key=True)
    location_name = Column(String, name='LocationName')
    x_coord = Column(Integer, name='XCoord')
    y_coord = Column(Integer, name='YCoord')
    location_type = Column(Enum(LocationTypeEnum), name='LocationType')


class Routes(Base):
    __tablename__ = 'routes'

    route_id = Column(Integer, name='RouteID', primary_key=True)
    from_location = Column(Integer, ForeignKey('locations.LocationID'), name='FromLocation')
    to_location = Column(Integer, ForeignKey('locations.LocationID'), name='ToLocation')
    time = Column(Integer, name="Time")


class Items(Base):
    __tablename__ = 'items'

    item_id = Column(Integer, name='ItemID', primary_key=True)
    item_name = Column(String)
    cost = Column(Integer, name='Cost')
    cost_to_sale = Column(Integer, name='CostToSale')
    item_type = Column(Enum(ItemTypeEnum), name='ItemType')
    hp = Column(Integer, name='HP')
    mana = Column(Integer, name='Mana')
    attack = Column(Integer, name='Attack')
    magic_attack = Column(Integer, name='MagicAttack')
    armour = Column(Integer, name='Armour')
    magic_armour = Column(Integer, name='MagicArmour')
    req_level = Column(Integer, name='ReqLevel')
    location_id = Column(Integer, ForeignKey('locations.LocationID'))


class Inventory(Base):
    __tablename__ = 'inventory'

    relation_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.UserID'))
    item_id = Column(Integer, ForeignKey('items.ItemID'))
    status = Column(Integer, default=0)
