from app import app, db
from app.models import User, Room


db.drop_all()
db.create_all()
if app.config['DEBUG']:
    print(app.config['DEBUG'])
    db.drop_all()
    db.create_all()
    testUsers = {
        'username': ['alice', 'bob', 'candice', 'tim'],
        'email': ['alice@example.com', 'bob@example.com', 'candice@example.com', 'tim@example.com'],
        'password': ['abc', 'def', 'ghi', 'tim']
    }
    r = Room(roomID='TEST', owner_id=1)
    for i in range(len(testUsers['username'])):
        u = User(username=testUsers['username'][i], email=testUsers['email'][i], order=i)
        u.set_password(testUsers['password'][i])
        db.session.add(u)
        r.players.append(u)
    db.session.add(r)
    db.session.commit()
