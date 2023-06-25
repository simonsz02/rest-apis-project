from db import db

# inheriting from db.Model, this class becomes a mapping between a row in a table to a Python class
class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)
    # SQLAlchemy knows that the stores table is used by the StoreModel class
    # when we have a store ID that is using the stores table, we can then define a relationship with the StoreModel class,
    # and it will automatically populate the store variable with StoreModel object, whose ID matches that of the foreign key.
    # back_populates="items" is gonna be used so that the StoreModel class will also have an items relationship
    store = db.relationship("StoreModel", back_populates="items")

    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")
     