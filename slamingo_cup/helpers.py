import config


def all_managers():
    return config.ACTIVE_MANAGERS + config.INACTIVE_MANAGERS


def sleeper_manager(display_name):
    return config.SLEEPER_MANAGERS.get(display_name, display_name)


def yahoo_manager(display_name):
    return config.YAHOO_MANAGERS.get(display_name, display_name)


def is_active(manager):
    return manager in config.ACTIVE_MANAGERS


def sleeper_leagues():
    return config.SLEEPER_LEAGUE_IDS


def yahoo_leagues():
    return config.YAHOO_LEAGUE_IDS


def get_in(json, path, default=None):
    for idx, key in enumerate(path, 1):
        if idx == len(path):
            return json.get(key, default)
        else:
            json = json[key]


def inclusive_range(start, end, steps=1):
    return range(start, end + 1, steps)
