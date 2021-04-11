from flask.blueprints import Blueprint


def create_api_blueprint(prefix: str, sufix: str = '', api_version=None):
  blueprint_name = '{0}_{1}_{2}'.format(prefix, sufix, api_version)

  if api_version is not None:
      url_prefix = '/{0}/{1}'.format(api_version, prefix)
  else:
      url_prefix = '/{0}'.format(prefix)

  return Blueprint(blueprint_name, blueprint_name, url_prefix=url_prefix)
