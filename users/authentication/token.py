from typing import Dict

import jwt

import settings


def generate_token(payload: Dict) -> str:
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def get_token_payload(token: str) -> Dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms='HS256')
