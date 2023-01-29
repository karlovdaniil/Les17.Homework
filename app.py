# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from create_data import Movie, Director, Genre

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Pluck(GenreSchema, 'name')
    director_id = fields.Int()
    director = fields.Pluck(DirectorSchema, 'name')


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        movies_query = db.session.query(Movie)

        director_id = request.args.get('director_id')
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get('genre_id')
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(movies_query.all()), 200

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)

        return 'Movie created', 201


@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        try:
            movie = db.session.query(Movie).get(uid)
            return movie_schema.dump(movie), 200

        except Exception as e:
            return f'{e} - Movie not found', 404

    def put(self, uid: int):
        updated_rows = db.session.query(Movie).filter(Movie.id == uid).update(request.json)

        if updated_rows != 1:
            return 'Not updated', 400

        db.session.commit()

        return f'Movie id={uid} - updated', 204

    def delete(self, uid: int):
        try:
            movie = db.session.query(Movie).get(uid)
            db.session.delete(movie)
            db.session.commit()

            return f'Movie id={uid} deleted', 204

        except Exception as e:
            return f'{e} - Movie not found', 404


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors), 200

    def post(self):
        request_json = request.json
        new_director = Director(**request_json)

        with db.session.begin():
            db.session.add(new_director)

        return 'Director created', 201


@directors_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):
        try:
            director = db.session.query(Director).get(uid)
            return director_schema.dump(director), 200

        except Exception as e:
            return f'{e} - Director not found', 404

    def put(self, uid: int):
        director = Director.query.get(uid)
        request_json = request.json

        if 'name' in request_json:
            director.name = request_json.get('name')

        db.session.add(director)
        db.session.commit()

        return 'Director updated', 204

    def delete(self, uid: int):
        try:
            director = db.session.query(Director).get(uid)
            db.session.delete(director)
            db.session.commit()

            return f'Director id={uid} deleted', 204

        except Exception as e:
            return f'{e} - Director not found', 404


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres), 200

    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)

        with db.session.begin():
            db.session.add(new_genre)

        return 'Genre created', 201


@genres_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        try:
            genre = db.session.query(Genre).get(uid)
            return genre_schema.dump(genre), 200

        except Exception as e:
            return f'{e} - Genre not found', 404

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        request_json = request.json

        if 'name' in request_json:
            genre.name = request_json.get('name')

        db.session.add(genre)
        db.session.commit()

        return 'Genre updated', 204

    def delete(self, uid: int):
        try:
            genre = db.session.query(Genre).get(uid)
            db.session.delete(genre)
            db.session.commit()

            return f'Genre id={uid} deleted', 204

        except Exception as e:
            return f'{e} - Genre not found', 404


if __name__ == '__main__':
    app.run(debug=True)
