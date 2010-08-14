# coding: utf-8

class ConfigNotFind(Exception):
    pass


def get_config(config_key, default_value=None):
    """
    get config value from config.py
    """
    try:
        import config
    except ImportError:
        if default_value is not None:
            return default_value
        raise ConfigNotFind

    if hasattr(config, config_key):
        return getattr(config, config_key)
    else:
        if default_value is not None:
            return default_value
        raise ConfigNotFind

