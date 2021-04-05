from sqlalchemy import Column, String

from ecommerce_api.model.base import ModelBase, AuditedModelBase
from ecommerce_api.resources import db


class User(AuditedModelBase, ModelBase, db.Model):
  username = Column(String(128))
  password = Column(String(128))
