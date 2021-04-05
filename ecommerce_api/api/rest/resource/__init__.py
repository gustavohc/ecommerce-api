from ecommerce_api.resources import db
from ecommerce_api.api import CrudResource


class BaseResource(CrudResource):
  def __init__(self, model):
    CrudResource.__init__(self, model, db.session)

  def make_errors_response(self, errors, status_code):
    """Retorna os erros no formato
    http://jsonapi.org/format/#error-objects"""

    formatted_errors = []

    for field_name, messages in errors.items():
        for message in messages:
            formatted_errors.append({
                'detail': message,
                'source': {
                    'pointer': '/data/attributes/' + field_name,
                },
            })

    response = {
        'errors': formatted_errors,
        'status': status_code,
    }

    return response, status_code

  def query(self):
    return super().query()

  def get_single(self, id):
    return super().get_single(id)
