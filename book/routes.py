from flask_restx import Namespace, Resource, fields
from flask import request
from services import enroll_user, list_books, borrow_book, get_book


api = Namespace('books', description='Book related operations')

user_model = api.model('User', {
    'name': fields.String(required=True, description='The user name'),
    'email': fields.String(required=True, description='The user email')
})

book_model = api.model('Book', {
    'title': fields.String(required=True, description='The book title'),
    'author': fields.String(required=True, description='The book author'),
    'publisher': fields.String(description='The book publisher'),
    'category': fields.String(description='The book category')
})

borrow_model = api.model('Borrow', {
    'user_id': fields.Integer(required=True, description='The user ID'),
    'days': fields.Integer(required=True, description='Number of days to borrow the book')
})

@api.route('/users')
class EnrollUser(Resource):
    @api.expect(user_model)
    @api.response(201, 'User enrolled successfully')
    def post(self):
        data = request.json
        new_user = enroll_user(data)
        return {'status': 'success', 'message': 'User enrolled successfully', 'data': new_user}, 201

@api.route('/')
class ListBooks(Resource):
    @api.param('publisher', 'Publisher of the book')
    @api.param('category', 'Category of the book')
    @api.response(200, 'Success')
    def get(self):
        publisher = request.args.get('publisher')
        category = request.args.get('category')
        books = list_books(publisher, category)
        return books, 200

@api.route('/<int:book_id>')
@api.param('book_id', 'The book identifier')
class GetBook(Resource):
    @api.expect(book_model)
    @api.response(200, 'Success')
    @api.response(404, 'Book not found')
    def get(self, book_id):
        book = get_book(book_id)
        return book, 200

@api.route('/borrow/<int:book_id>')
@api.param('book_id', 'The book identifier')
class BorrowBook(Resource):
    @api.expect(borrow_model)
    @api.response(200, 'Book borrowed successfully')
    @api.response(400, 'Invalid input')
    def post(self, book_id):
        data = request.json
        user_id = data['user_id']
        days = data['days']
        response, status_code = borrow_book(book_id, user_id, days)
        return response, status_code
