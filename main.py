from app import app, db
from app.models import User, Service, Comment, Business

@app.shell_context_processor
def shell_cont():
    return {'db': db, 'User': User, 'Service': Service, 'Comment': Comment, 'Business': Business}

if __name__ == '__main__':
    app.run(debug=True)
