
from flask_restx import Resource, fields, Namespace
from flask import request
from services import add_book, remove_book, list_users, list_borrowings, list_unavailable_books


api = Namespace('books', description='Admin related operations')

book_model = api.model('Book', {
    'title': fields.String(required=True, description='The book title'),
    'author': fields.String(required=True, description='The book author'),
    'published_date': fields.String(required=True, description='The book published date')
})

@api.route('/')
class BookList(Resource):
    # @api.doc('list_books')
    # def get(self):
    #     """List all books"""
    #     return jsonify(list_books())

    @api.doc('add_book')
    @api.expect(book_model)
    def post(self):
        """Add a new book"""
        data = request.get_json()
        new_book = add_book(data)
        return {'status': 'success', 'message': 'Book added successfully', 'data': new_book}, 201

@api.route('/<int:book_id>')
@api.response(404, 'Book not found')
@api.param('book_id', 'The book identifier')
class Book(Resource):
    @api.doc('delete_book')
    def delete(self, book_id):
        """Delete a book given its identifier"""
        deleted_book = remove_book(book_id)
        if deleted_book:
            return {'message': 'Book removed successfully', 'data': deleted_book}, 200
        else:
            return {'message': 'Book not found'}, 400

@api.route('/users')
class UserList(Resource):
    @api.doc('list_users')
    @api.response(200, 'Success')
    def get(self):
        """List all users"""
        users = list_users()
        return users, 200

@api.route('/borrowings')
class BorrowingList(Resource):
    @api.doc('list_borrowings')
    @api.response(200, 'Success')
    def get(self):
        """List all borrowings"""
        borrow_records = list_borrowings()
        return borrow_records, 200

@api.route('/unavailable')
class UnavailableBooks(Resource):
    @api.doc('list_unavailable_books')
    @api.response(200, 'Success')
    def get(self):
        """List all unavailable books"""
        books = list_unavailable_books()
        return books, 200

