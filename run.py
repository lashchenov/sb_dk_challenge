from bookstore.bookstore import app
from bookstore.util import sanic_config_manager


sanic_config_manager(app, prefix="SANIC_")


if __name__ == "__main__":

    app.run()

