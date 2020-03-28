# WebMJ: A WebApp to play Mahjong

A simple html based way to play Mahjong online!
WebMJ uses a ```Python-Flask``` backend with asynchronous websocket communication via ```Socket.IO```.

## Requirements:
- ```Python 3.x```
- ```Flask```
  - ```Flask-Socketio```
  - ```Flask-Login```
  - ```Flask-SQLAlchemy```
- ```NumPy``` 

## TODO:
- Test win conditions
- Handle win events:
  - decide next dealer,
  - deal new tiles,
  - refresh clients
  - (calculate points for winner)
  - (handle multiple winning combinations)
- Handle refresh events:
  - Show Win options
- Add database logging of games 
