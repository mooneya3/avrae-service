import requests
from flask import abort, current_app, request

DISCORD_API = "https://discordapp.com/api/v6"
DISCORD_CDN = "https://cdn.discordapp.com"
HEADERS = {
    "User-Agent": "DiscordBot (https://github.com/avrae/avrae.io, 1)"
}


class UserInfo:
    def __init__(self, user):
        self.username = user['username']
        self.id = user['id']
        self.discriminator = user['discriminator']
        self.avatar = user['avatar']

    def get_avatar_url(self):
        if self.avatar:
            return f"{DISCORD_CDN}/avatars/{self.id}/{self.avatar}.png?size=512"
        else:
            return f"{DISCORD_CDN}/embed/avatars/{int(self.discriminator) % 5}.png?size=512"

    def to_dict(self):
        return {'id': self.id, 'username': f"{self.username}#{self.discriminator}", 'avatarUrl': self.get_avatar_url()}


def get(endpoint, token):
    headers = HEADERS.copy()
    headers['Authorization'] = f"Bearer {token}"
    return requests.get(f"{DISCORD_API}{endpoint}", headers=headers)


def get_user_info():
    token = None
    try:
        token = request.headers['Authorization']
    except KeyError:
        abort(403)
    r = get("/users/@me", token)
    try:
        data = r.json()
        # cache us
        current_app.mdb.users.insert_one(data)
        return UserInfo(data)
    except KeyError:
        abort(403)


def fetch_user_info(user_id):
    # is user in our list of known users?
    user = current_app.mdb.users.find_one({"id": str(user_id)})
    if user is not None:
        del user['_id']  # mongo ID
        return UserInfo(user)
    else:
        return UserInfo({"username": str(user_id), "id": str(user_id), "discriminator": "0000", "avatar": None})
