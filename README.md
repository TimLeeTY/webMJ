# WebMJ: A WebApp to play Mahjong

A simple html based way to play Mahjong online!
WebMJ uses a `Python-Flask` backend with asynchronous websocket communication via `Socket.IO`.

Deployed on [Heroku](https://web-mj.herokuapp.com)!

## Requirements:
- `Python 3.6`
- `Flask`
  - `Flask-Socketio`
  - `Flask-Login`
  - `Flask-SQLAlchemy`
- `NumPy`

## TODO:
- Other players' tiles not displaying properly after set event
- Implement 'addgong' check to every turn 
- Handle win events:
  - ~~(calculate points for winner)~~
  - Show winning points on client side
- Add indicators for actions taken
- Logic to handle running out of tiles *(added, needs testing)*
- Add flowers
- Add screenshots to readme


