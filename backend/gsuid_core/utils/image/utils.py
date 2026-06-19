def sget(d, key, default=None):
    """Safe dict get."""
    if isinstance(d, dict):
        return d.get(key, default)
    return default
