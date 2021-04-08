from datetime import datetime
from sqlalchemy import Column, DateTime, event, Integer


class ModelBase():
  """Define as colunas utilizadas em todas as tabelas do modelo

  Returns:
      str -- retorna uma descrição do objeto
  """
  id = Column(Integer, primary_key=True, autoincrement=True)


class AuditedModelBase():
  """Define as colunas utilizadas para autoria nos registros da base
  """

  created_at = Column(DateTime, nullable=False)
  updated_at = Column(DateTime, nullable=True)

  @staticmethod
  def audit_on_insert(mapper, connection, target):
    if target.created_at is None:
        target.created_at = datetime.utcnow()
    if target.updated_at is None:
        target.updated_at = datetime.utcnow()

  @staticmethod
  def audit_on_update(mapper, connection, target):
      target.updated_at = datetime.utcnow()

  @classmethod
  def __declare_last__(cls):
    event.listen(cls, 'before_insert', cls.audit_on_insert)
    event.listen(cls, 'before_update', cls.audit_on_update)
