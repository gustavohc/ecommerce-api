import abc
import logging

from flask import Blueprint, jsonify, request
from flask_restful import Resource
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

LOGGER = logging.getLogger("crud-resource")

def _unauthorized():
    return {'error': 'Unauthorized'}, 401


class CrudResource(Resource):
    """
    Resouce base que já disponibiliza um CRUD para determinado modelo.
    """

    def __init__(self, model, session):
        self.model = model
        self.session = session

    def _methods(self):
        """
        Métodos que estão disponíveis para o recurso.
        """

        return {
            'QUERY': False,
            'GET': False,
            'POST': False,
            'PATCH': False,
            'DELETE': False
        }

    @abc.abstractmethod
    def _schema(self, method):
        """
        Usar essa função para retornar o schema que deverá ser utilizado.
        """

        return None

    def _to_dict(self, resource):
            data = dict(resource.__dict__)

            relations = [rel[0] for rel in resource.__class__.__mapper__.relationships.items()]

            for rel in relations:
                try:
                    data[rel] = getattr(resource, rel)

                    if data[rel]:
                        data[rel] = dict(data[rel].__dict__)

                except Exception as e:
                    LOGGER.info('Exception CrudResource._to_dict: %s' % str(e))

            return data

    def _remove_fields(self, result, fields=None):
        if not fields:
            if 'fields' not in request.args:
                return result

            fields = request.args.get('fields').split(',')

        def exclude(result):
            nesteds = {}
            new_result = {}
            for field in fields:
                field = field.strip()
                if '.' in field:
                    split = field.split('.', 1)
                    if not nesteds.get(split[0]):
                        nesteds[split[0]] = []
                    nesteds[split[0]].append(split[1])
                elif field in result:
                    new_result[field] = result[field]

            for nested in nesteds:
                if nested in result:
                    new_result[nested] = self._remove_fields(result[nested], fields=nesteds[nested])
            return new_result

        if isinstance(result, dict):
            return exclude(result)

        elif isinstance(result, list):
            new_results = []
            for result in result:
                new_results.append(exclude(result))
            return new_results

        return result

    def _define_search_order(self, query, schema, model=None, orders=None, deep=0):
        """
        Define a ordem da consulta baseado no parametro da request `order`.
        Obs.: Essa função será chamada apenas se nenhuma ordem for definida na função `_make_query` .
        """

        if not model:
            model = self.model

        if not orders:
            # A ordem padrão será a data de criação do recurso.
            orders = request.args.get('order', 'created_at').split(',')

        order_by = []
        for order in orders:
            field = order.strip()
            if '.' in field and deep < 4:
                split = field.split('.', 1)
                if split[0].startswith('-'):
                    nested_field = split[0][1:]
                    nested_orders = ['-' + split[1]]
                else:
                    nested_field = split[0]
                    nested_orders = [split[1]]

                if hasattr(model, nested_field) and nested_field in schema.fields:
                    try:
                        nested_model = inspect(model.__dict__[nested_field]).mapper.class_
                        if not nested_model in [c.entity for c in query._join_entities]:
                            query = query.join(model.__dict__[nested_field])

                        # Recursão para entrar no campo
                        query, nested_order_by = self._define_search_order(query, schema.fields[nested_field].schema, nested_model, nested_orders, deep=deep+1)
                        order_by.extend(nested_order_by)
                    except Exception as ex:
                        continue
            else:
                if field.startswith('-'):
                    if hasattr(model, field[1:]) and field[1:] in schema.fields:
                        order_by.append(model.__dict__[field[1:]].desc())
                else:
                    if hasattr(model, field) and field in schema.fields:
                        order_by.append(model.__dict__[field].asc())
        return query, order_by

    
    def _integrity_error_msg(self, resource, ex):
        return 'IntegrityError'
    
    def _authorize_resource(self, method, resource):
        return True
    
    def _make_query(self, query):
        """
        Classes filhas poderão sobreecrever essa função para construir a query.
        Caso contrário, todos os registros serão retornados.
        """
        return query

    @abc.abstractmethod
    def _before_post(self, resource):
        return

    @abc.abstractmethod
    def _before_patch(self, resource, old_resource):
        return

    @abc.abstractmethod
    def _before_delete(self, resource):
        return

    @abc.abstractmethod
    def _after_get(self, resource, result):
        return

    @abc.abstractmethod
    def _after_query(self, results, objects):
        return

    @abc.abstractmethod
    def _after_post(self, resource, result):
        return

    @abc.abstractmethod
    def _after_patch(self, resource, old_resource, result):
        return

    @abc.abstractmethod
    def _after_delete(self, old_resource, result):
        return
    
    def post(self):
        methods = self._methods()
        if not methods.get('POST') is True:
            return _unauthorized()

        schema = self._schema('POST')()
        schema.context = self

        try:
            data = schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return err.messages, 400

        resource = self.model()
        resource.__dict__.update(data)

        resp = self._before_post(resource)
        if resp:
            return resp

        if not self._authorize_resource('POST', resource):
            return _unauthorized()

        try:
            self.session.add(resource)
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            LOGGER.exception(ex)
            return {'error': self._integrity_error_msg(resource, ex)}, 422

        result = schema.dump(resource)

        self._after_post(resource, result)

        return result, 201

    def patch(self, id=None):
        methods = self._methods()
        if not methods.get('PATCH') is True:
            return _unauthorized()

        if not id:
            return 'Bad request', 400

        resource = None

        if id:
            resource = self.session.query(self.model).get(id)

        if not resource:
            return 'Resource not found', 404

        old_resource = self._to_dict(resource)

        patch = request.get_json(silent=True) or {}

        schema = self._schema('PATCH')
        load_schema = schema(only=patch.keys())
        schema = schema()
        schema.context = self

        schema_fields = schema.fields.keys()

        for patch_field in patch.keys():
            if patch_field not in schema_fields:
                return 'Bad request', 400
            elif schema.fields[patch_field].dump_only:
                return 'Bad request', 400

        try:
            data = load_schema.load(patch)
        except ValidationError as err:
            return err.messages, 400

        for attr in data:
            if hasattr(resource, attr):
                setattr(resource, attr, data[attr])

        resp = self._before_patch(resource, old_resource)
        if resp:
            return resp

        if not self._authorize_resource('PATCH', resource):
            return _unauthorized()

        self.session.add(resource)

        try:
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            return {'error': self._integrity_error_msg(resource, ex)}, 422

        result = schema.dump(resource)

        self._after_patch(resource, old_resource, result)

        return result, 200

    def delete(self, id=None):
        methods = self._methods()
        if not methods.get('DELETE') is True:
            return _unauthorized()

        if id:
            resource = None

            if id:
                resource = self.session.query(self.model).get(id)

            if not resource:
                return 'Resource not found', 404

            self._before_delete(resource)

            if not self._authorize_resource('DELETE', resource):
                return _unauthorized()

            schema = self._schema('DELETE')()
            schema.context = self

            result = schema.dump(resource)

            # Forma antiga não executa os relacionamentos python
            # e desssa forma não faz o delete casacade
            # self.session.query(self.model).filter(self.model.__dict__['id'] == resource.id).delete()
            # Dessa forma os relacionamentos são executados
            self.session.delete(resource)
            self.session.commit()
            self._after_delete(resource, result)
            return result

    def get_single(self, id):
        methods = self._methods()
        if not methods.get('GET') is True:
            return _unauthorized()
        resource = None

        if id:
            resource = self.session.query(self.model).filter(self.model.id == id).first()

        if not resource:
            return 'Resource not found', 404

        if not self._authorize_resource('GET', resource):
            return _unauthorized()

        schema = self._schema('GET')

        result = schema().dump(resource)

        self._after_get(resource, result)

        return self._remove_fields(result)

    def query(self):
        methods = self._methods()
        if not methods.get('QUERY') is True:
            return _unauthorized()

        schema = self._schema('QUERY')(many=True)
        schema.context = self

        query = self.session.query(self.model)
        query = self._make_query(query)

        # Paginação
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        if not limit == 0:
            if request.args.get('max_results') and request.args.get('max_results').isnumeric():
                max_results = int(request.args.get('max_results'))
                num_results = query.limit(max_results).count()
            else:
                num_results = query.count()

            total_pages = (num_results // limit) if num_results > 0 else 0
            if total_pages > 0 and (num_results % limit) > 0:
                total_pages += 1
            elif total_pages == 0:
                total_pages = 1

            if not query._order_by:
                query, order_by = self._define_search_order(query, schema)

                if order_by:
                    query = query.order_by(*order_by)

            results = query.limit(limit).offset((page - 1) * limit).all()
        else:
            results = query.all()

        objects = schema.dump(results)
        objects = self._remove_fields(objects)

        self._after_query(results, objects)

        if limit == 0:
            return jsonify({
                'objects': objects,
            })

        return jsonify({
            'objects': objects,
            'page': page,
            'num_results': num_results,
            'total_pages': total_pages
        })

    def get(self, id=None):
        if id:
            return self.get_single(id)
        else:
            return self.query()
