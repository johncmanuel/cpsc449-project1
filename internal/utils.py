import os


def get_env_var(env_var):
    try:
        return os.getenv(env_var)
    except KeyError:
        raise Exception(f"{env_var} not found in your .env file!")
