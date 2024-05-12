import json, yaml
import os

import requests as requests
from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Todo API',
          description='A simple Todo API',
          )

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details')
})


class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    # def create_yaml(self):
    #     swagger_json = api.__schema__
    #
    #     # Convert JSON to YAML
    #     yaml_data = yaml.dump(swagger_json, default_flow_style=False)
    #
    #     # Save YAML data to a file in the same directory
    #     file_path = 'swagger.yaml'
    #     with open(file_path, 'w') as yaml_file:
    #         yaml_file.write(yaml_data)

    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        self.todos.append(todo)
        return todo

    def update(self, id, data):
        todo = self.get(id)
        todo.update(data)
        return todo

    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)


DAO = TodoDAO()
DAO.create({'task': 'Build an API'})
DAO.create({'task': '?????'})
DAO.create({'task': 'profit!'})
# DAO.create_yaml()


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''

    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        data = json.loads(json.dumps(api.__schema__))
        with open('yamldoc.yml', 'w') as yamlf:
            yaml.dump(data, yamlf, allow_unicode=True, default_flow_style=False)
        return DAO.todos

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''

    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)


# # Generate YAML file on startup
# def generate_yaml():
#     with app.app_context():
#         # Generate Swagger JSON
#         swagger_json = api.__schema__
#
#         # Convert JSON to YAML
#         yaml_data = yaml.dump(swagger_json, default_flow_style=False)
#
#         # Save YAML data to a file in the same directory
#         file_path = 'swagger.yaml'
#         with open(file_path, 'w') as yaml_file:
#             yaml_file.write(yaml_data)
#
#
# generate_yaml()
# from flask import Flask, after_this_request, send_file, safe_join, abort


# @api.route('/swagger.yml')
# class HelloWorld(Resource):
#     def get(self):
#         data = json.loads(json.dumps(api.__schema__))
#         with open('yamldoc.yml', 'w') as yamlf:
#             yaml.dump(data, yamlf, allow_unicode=True, default_flow_style=False)
#             file = os.path.abspath(os.getcwd())


if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context(), app.test_request_context():
        data = json.loads(json.dumps(api.__schema__))
        with open('yamldoc.yml', 'w') as yamlf:
            yaml.dump(data, yamlf, allow_unicode=True, default_flow_style=False)
