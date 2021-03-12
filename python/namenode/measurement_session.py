session_settings = {}

def put_setting(key, val):
    session_settings[key] = val

def get_settings():
    return session_settings

def clear_session():
    session_settings = {}