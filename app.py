from flask import Flask, jsonify
from flask.views import MethodView
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

# MODELS


db = SQLAlchemy(app)

# MODELS
@dataclass
class User(db.Model):
    id: int
    email: str

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)


@dataclass
class Publications(db.Model):
    id: int
    title: str

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


@dataclass
class Stories(db.Model):
    id: int
    title: str

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


@dataclass
class StoryCategories(db.Model):
    id: int
    title: str

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


@dataclass
class UserBookmarks(db.Model):
    id: int
    # title: str

    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String, nullable=False)


@dataclass
class Podcasts(db.Model):
    id: int
    title: str

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


@dataclass
class EditorsChoice(db.Model):
    id: int
    # title: str

    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String, nullable=False)


@dataclass
class Sections(db.Model):
    id: int
    # title: str

    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String, nullable=False)


@dataclass
class ContentSections(db.Model):
    id: int
    title: str

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


# Decorators


def user_required(f):
    """Checks whether user is logged in or raises error 401."""

    def decorator(*args, **kwargs):
        print("user_required decorator triggered!")
        return f(*args, **kwargs)

    return decorator


def admin_required(f):
    """Checks whether user is logged in or raises error 401."""

    def decorator(*args, **kwargs):
        print("admin_required decorator triggered!")
        return f(*args, **kwargs)

    return decorator


# Base API Views
class PublicListDetailView(MethodView):
    model = None

    def get(self, entry_id):
        if entry_id is None:
            result = self.model.query.all()
        else:
            result = self.model.query.get(entry_id)
        return jsonify(result)


class UserAuthCUDView(MethodView):
    model = None
    decorators = [user_required]

    def post(self):
        # create a new entry
        new_entry = self.model(**request.get_json())
        db.session.add(new_entry)
        db.session.commit()
        return "OK"

    def delete(self, entry_id):
        # delete a single entry
        entry = self.model.query.get(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return "OK"

    def put(self, entry_id):
        # update a single entry
        pass


class AdminCrudView(UserAuthCUDView):
    decorators = [admin_required]


# REST APIs
class PublicationsAPI(UserAuthCUDView, PublicListDetailView):
    model = Publications


class StoriesAPI(UserAuthCUDView, PublicListDetailView):
    model = Stories


class UserBookmarksAPI(UserAuthCUDView, PublicListDetailView):
    model = UserBookmarks


class PodcastsAPI(AdminCrudView, PublicListDetailView):
    model = Podcasts


class StoryCategoriesAPI(UserAuthCUDView, PublicListDetailView):
    model = StoryCategories


class EditorsChoiceAPI(AdminCrudView, PublicListDetailView):
    model = EditorsChoice


class SectionsAPI(AdminCrudView, PublicListDetailView):
    model = Sections


class ContentSectionsAPI(AdminCrudView, PublicListDetailView):
    model = ContentSections


# fmt: off

def register_api(view, endpoint, url):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={'entry_id': None}, view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    # Creates a rule like: '/podcasts/<int:entry_id>'
    app.add_url_rule(f'{url}<int:entry_id>', view_func=view_func, methods=['GET', 'PUT', 'DELETE'])

# Register APIs

register_api(PublicationsAPI, 'publications_api', '/publications/')
register_api(PodcastsAPI, 'podcasts_api', '/podcasts/')
register_api(StoriesAPI, 'stories_api', '/stories/')
register_api(UserBookmarksAPI, 'user_bookmarks_api', '/bookmarks/')
register_api(StoryCategoriesAPI, 'story_categories_api', '/categories/')
register_api(EditorsChoiceAPI, 'editors_choice_api', '/editors-choice/')
register_api(SectionsAPI, 'sections_api', '/sections/')
register_api(ContentSectionsAPI, 'content_sections_api', '/content-sections/')

# user_view = PublicationsAPI.as_view('publications_api')
# app.add_url_rule('/publications/', defaults={'entry_id': None}, view_func=user_view, methods=['GET',])
# app.add_url_rule('/publications/', view_func=user_view, methods=['POST',])
# app.add_url_rule('/publications/<int:entry_id>', view_func=user_view, methods=['GET', 'PUT', 'DELETE'])

# podcast_view = PodcastsAPI.as_view('podcasts_api')
# app.add_url_rule('/podcasts/', defaults={'entry_id': None}, view_func=podcast_view, methods=['GET',])
# app.add_url_rule('/podcasts/', view_func=podcast_view, methods=['POST',])
# app.add_url_rule('/podcasts/<int:entry_id>', view_func=podcast_view, methods=['GET', 'PUT', 'DELETE'])


# fmt: on


@app.route("/")
def hello_world():
    return "Hello, World!"


db.create_all()

if __name__ == "__main__":
    app.run(debug=True)