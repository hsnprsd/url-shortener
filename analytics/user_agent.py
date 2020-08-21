from flask import request


def get_request_device_type() -> str:
    return request.user_agent.platform or "other"


def get_request_browser_type() -> str:
    return request.user_agent.browser or "other"


def get_request_ip() -> str:
    return request.remote_addr
