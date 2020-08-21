from flask import Flask, request, redirect

from analytics import service as analytics_service
from shortening import service as shortening_service
from shortening.exceptions import URLNotFound
from users import service as registration_service
from users.authentication import service as authentication_service
from users.authentication.decorator import is_authenticated
from users.authentication.exceptions import UserNotFound
from users.exceptions import UserAlreadyExists

server = Flask(__name__)


@server.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        username = str(data['username'])
        password = str(data['password'])
    except KeyError:
        return "", 400

    try:
        jwt_token = authentication_service.login(username, password)
    except UserNotFound:
        return "", 404

    return jwt_token, 200


@server.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        username = str(data['username'])
        password = str(data['password'])
    except KeyError:
        return "", 400

    try:
        registration_service.register(username, password)
    except UserAlreadyExists:
        return "", 409

    return "", 200


@server.route('/urls', methods=['GET', 'POST'])
@is_authenticated
def make_url_short(user):
    if request.method == 'GET':
        urls = shortening_service.get_urls_by_user(user)

        response = {
            'urls': [],
        }

        for url in urls:
            response['urls'].append({
                'url': url.actual_url,
                'token': url.short_token,
            })

        return response, 200

    if request.method == 'POST':
        data = request.get_json()
        try:
            url = str(data['url'])
        except KeyError:
            return "", 400

        try:
            shortened_url = shortening_service.make_url_short(
                user=user,
                url=url,
            )
        except UserAlreadyExists:
            return "", 409

        return {'shortened_url': shortened_url}, 200


@server.route('/urls/<short_token>', methods=['GET'])
def redirect_url(short_token):
    actual_url = shortening_service.get_actual_url_for_short_token(
        short_token,
    )
    shortening_service.dispatch_redirect_event(short_token)
    return redirect(actual_url)


@server.route('/urls/<short_token>/analytics', methods=['GET'])
@is_authenticated
def get_analytics_of_shortened_url(user, short_token):
    try:
        response = {
            'analytics': analytics_service.get_url_analytics(
                user,
                short_token,
            ),
        }
    except URLNotFound:
        return {}, 404

    return response, 200


if __name__ == '__main__':
    server.run()
