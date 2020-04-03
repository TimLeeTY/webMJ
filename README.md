# WebMJ: A WebApp to play Mahjong

A simple html based way to play Mahjong online!
WebMJ uses a `Python-Flask` backend with asynchronous websocket communication via `Socket.IO`.

## Requirements:
- `Python 3.x`
- `Flask`
  - `Flask-Socketio`
  - `Flask-Login`
  - `Flask-SQLAlchemy`
- `NumPy`

## TODO:
- Handle win events:
  - (currently `whoseTurn` and `addSets` are still not working properly
  - (calculate points for winner)
  - (handle multiple winning combinations)
- Add indicators for actions taken
- Reverse sorting on hand
- Logic to handle running out of tiles
- Add flowers

