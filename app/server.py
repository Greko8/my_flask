import flask
from errors import HttpError
from flask import jsonify, request, views
from flask_bcrypt import Bcrypt
from models import Session, User, Ad
from schema import CreateAd, UpdateAd, CreateUser, UpdateUser
from sqlalchemy.exc import IntegrityError
from tools import validate

app = flask.Flask("app")
bcrypt = Bcrypt(app)

def hash_password(password: str):
    password = password.encode()
    return bcrypt.generate_password_hash(password).decode()


def check_password(password: str, hashed_password: str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.check_password_hash(password, hashed_password)


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response: flask.Response):
    request.session.close()
    return response


@app.errorhandler(HttpError)
def error_handler(error):
    response = jsonify({"error": error.description})
    response.status_code = error.status_code
    return response

def get_user(user_id: int):
    user = request.session.get(User, user_id)
    if user is None:
        raise HttpError(404, "user not found")
    return user


def add_user(user: User):
    try:
        request.session.add(user)
        request.session.commit()
    except IntegrityError as err:
        raise HttpError(409, "user already exists")

def get_ad(ad_id: int):
    ad = request.session.get(Ad, ad_id)
    if ad is None:
        raise HttpError(404, "add not found")
    return ad


def add_ad(ad: Ad):
    try:
        request.session.add(ad)
        request.session.commit()
    except IntegrityError as err:
        raise HttpError(409, "ad already exists")

class UserView(views.MethodView):
    @property
    def session(self) -> Session:
        return request.session

    def get(self, user_id: int):
        user = get_user(user_id)
        return jsonify(user.dict)

    def post(self):
        user_data = validate(CreateUser, request.json)
        user_data["password"] = hash_password(user_data["password"])
        user = User(**user_data)
        add_user(user)
        return jsonify({"id": user.id})

    def patch(self, user_id: int):
        user = get_user(user_id)
        user_data = validate(UpdateUser, request.json)
        if "password" in user_data:
            user_data["password"] = hash_password(user_data["password"])
        for key, value in user_data.items():
            setattr(user, key, value)
            add_user(user)
        return jsonify({"id": user.id})

    def delete(self, user_id: int):
        user = get_user(user_id)
        self.session.delete(user)
        self.session.commit()
        return jsonify({"status": "ok"})

class AdView(views.MethodView):
    @property
    def session(self) -> Session:
        return request.session

    def get(self, ad_id: int):
        ad = get_ad(ad_id)
        return jsonify(ad.dict)

    def post(self):
        ad_data = validate(CreateAd, request.json)
        ad = Ad(**ad_data)
        get_user(ad.owner_id)
        add_ad(ad)
        return jsonify({"id": ad.id})

    def patch(self, ad_id: int):
        ad = get_ad(ad_id)
        ad_data = validate(UpdateAd, request.json)
        for key, value in ad_data.items():
            setattr(ad, key, value)
            add_ad(ad)
        return jsonify({"id": ad.id})

    def delete(self, ad_id: int):
        ad = get_ad(ad_id)
        self.session.delete(ad)
        self.session.commit()
        return jsonify({"status": "ok"})

user_view = UserView.as_view("user_view")
ad_view = AdView.as_view("ad_view")

app.add_url_rule(
    "/ads/<int:ad_id>", view_func=ad_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/ads", view_func=ad_view, methods=["POST"])
app.add_url_rule(
    "/users/<int:user_id>", view_func=user_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/users", view_func=user_view, methods=["POST"])

if __name__ == "__main__":
    app.run()
