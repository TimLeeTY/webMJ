from app import app, db
from app.models import User


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


if __name__ == '__main__':
    db.create_all()
    if app.config['DEBUG']:
        db.drop_all()
        testUsers = {
            'username': ['alice', 'bob', 'candice', 'tim'],
            'email': ['alice@example.com', 'bob@example.com', 'candice@example.com', 'tim@example.com'],
            'password': ['abc', 'def', 'ghi', 'tim']
        }
        for i in range(len(testUsers['username'])):
            u = User(username=testUsers['username'][i], email=testUsers['email'][i])
            u.set_password(testUsers['password'][i])
            db.session.add(u)
            db.session.commit()
    app.run()
