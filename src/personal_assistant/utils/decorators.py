from functools import wraps


def input_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            return f"Value error: {error}"
        except KeyError as error:
            return f"Key error: {error}"
        except IndexError as error:
            return f"Index error: {error}"
        except Exception as error:
            return f"Unexpected error: {error}"

    return wrapper
