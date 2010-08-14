# coding: utf-8

class SettingsNotFind(Exception):
    pass


def get_settings(settings_key, default_value=None):
    """
    get settings value from settings.py
    """
    try:
        import settings
    except ImportError:
        if default_value is not None:
            return default_value
        raise SettingsNotFind

    if hasattr(settings, settings_key):
        return getattr(settings, settings_key)
    else:
        if default_value is not None:
            return default_value
        raise SettingsNotFind

