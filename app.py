from flask import Flask, jsonify
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

db = SQLAlchemy(app)
ma = Marshmallow(app)

"""
    Models and Schemas
"""


class Publications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


class PublicationsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Publications


class Stories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=True)


class StoriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Stories


class StoryCategories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


class StoryCategoriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StoryCategories


class UserBookmarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String, nullable=False)


class UserBookmarksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserBookmarks


class Podcasts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


class PodcastsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Podcasts


class EditorsChoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String, nullable=False)


class EditorsChoiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EditorsChoice


class Sections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String, nullable=False)


class SectionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sections


class ContentSections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


class ContentSectionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ContentSections


"""
    Decorators
"""


def user_required(f):
    """Checks whether user is logged in."""

    def decorator(*args, **kwargs):
        print("user_required decorator triggered!")
        return f(*args, **kwargs)

    return decorator


def admin_required(f):
    """Checks whether user is admin."""

    def decorator(*args, **kwargs):
        print("admin_required decorator triggered!")
        return f(*args, **kwargs)

    return decorator


"""
    Base API Views
"""


class BaseView(MethodView):
    _model = None
    _schema = None

    def __init__(self):
        """
        If _schema is not declared when extending this class, try to find a class with 'Schema' suffix.
        Ex: Stories -> StoriesSchema
        This is handy because we can declare only the _model and it will try find its related schema class."""
        if self._schema is None:
            _cls_name = f"{self._model.__name__}Schema"
            self._schema = globals()[_cls_name]


class PublicListReadView(BaseView):
    def get(self, entry_id):
        # Handle any '?fields=' params received in the request - Ex: /stories/?fields=title,id
        fields = request.args.get("fields")
        if fields:
            schema = self._schema(only=fields.split(","))
        else:
            schema = self._schema()

        # Query database and return data
        if entry_id is None:
            # Return list of all entries
            result = self._model.query.all()
            return jsonify(schema.dump(result, many=True))
        else:
            # Return a single object
            result = self._model.query.get(entry_id)
            return jsonify(schema.dump(result))


class UserAuthCUDView(BaseView):
    decorators = [user_required]

    def post(self):
        # create a new entry
        new_entry = self._model(**request.get_json())
        db.session.add(new_entry)
        db.session.commit()
        schema = self._schema()
        return jsonify(schema.dump(new_entry))

    def delete(self, entry_id):
        # delete a single entry
        entry = self._model.query.get(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return {"msg": "Entry successfully deleted."}, 200

    def put(self, entry_id):
        # update a single entry
        raise NotImplementedError


class AdminCUDView(UserAuthCUDView):
    decorators = [admin_required]


"""
    APIs
    Keep in mind that we can override any method (GET, POST, etc) if necessary
"""


class PublicationsAPI(UserAuthCUDView, PublicListReadView):

    _model = Publications


class StoriesAPI(UserAuthCUDView, PublicListReadView):
    _model = Stories


class UserBookmarksAPI(UserAuthCUDView, PublicListReadView):
    _model = UserBookmarks


class PodcastsAPI(AdminCUDView, PublicListReadView):
    _model = Podcasts


class StoryCategoriesAPI(UserAuthCUDView, PublicListReadView):
    _model = StoryCategories


class EditorsChoiceAPI(AdminCUDView, PublicListReadView):
    _model = EditorsChoice


class SectionsAPI(AdminCUDView, PublicListReadView):
    _model = Sections


class ContentSectionsAPI(AdminCUDView, PublicListReadView):
    _model = ContentSections


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


# If we weren't using the custom register_api() function, this is how we would go about registering each of our APIs:

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