from db import db

class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    # back_populates="items" is gonna be used so that the StoreModel class will also have an items relationship

    # lazy=dynamic means that the item here are not going to be fetched from the database until we tell it to
    # cascade: when we delete a store, its items will be deleted as well.
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete")

    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")