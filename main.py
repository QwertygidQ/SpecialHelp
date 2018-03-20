from app import app, db
from app.models import User, Tag, Comment, Business
import config
import sys


@app.shell_context_processor
def shell_cont():
    return {'db': db, 'User': User, 'Tag': Tag, 'Comment': Comment, 'Business': Business}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].isdigit() and 1 < int(sys.argv[1]) < 65535:
        config.port = int(sys.argv[1])
    app.run(host=config.host, port=config.port, debug=config.debug)
