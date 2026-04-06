import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table, Enum
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class ContactType(enum.Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"
    OTHER = "other"


staff_group = Table(
    'staff_group_association', Base.metadata,
    Column('staff_id', Integer, ForeignKey('staff.id', ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete="CASCADE"))
)


class Staff(Base):
    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    contacts = relationship("StaffContact", back_populates="owner", cascade="all, delete-orphan")
    groups = relationship("Group", secondary=staff_group, back_populates="members")


class StaffContact(Base):
    __tablename__ = 'staff_contacts'

    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff.id', ondelete="CASCADE"))
    value = Column(String, nullable=False) # 'admin@mail.ru'
    type = Column(Enum(ContactType), nullable=False, default=ContactType.EMAIL)

    owner = relationship("Staff", back_populates="contacts")


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False) # 'admins', 'engineers'

    members = relationship("Staff", secondary=staff_group, back_populates="groups")