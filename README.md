# WebMJ: A WebApp to play Mahjong

A simple html based way to play Mahjong online!
WebMJ uses a `Python-Flask` backend with asynchronous websocket communication via `Socket.IO`.

Deployed on [Heroku](https://web-mj.herokuapp.com)!

## Requirements:
- `Python 3.x`
- `Flask`
  - `Flask-Socketio`
  - `Flask-Login`
  - `Flask-SQLAlchemy`
- `NumPy`

## TODO:
- Handle win events:
  - ~~(currently `whoseTurn` and `addSets` are still not working properly~~ (fixed?)
  - (calculate points for winner)
- Add indicators for actions taken
- Logic to handle running out of tiles *(added, needs testing)*
- Add flowers

