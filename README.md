# WebMJ: A WebApp to play Mahjong

A simple html based way to play Mahjong online!
WebMJ uses a `Python-Flask` backend with asynchronous websocket communication via `Socket.IO`.

Deployed on [Heroku](https://web-mj.herokuapp.com)!

## Screenshots:

![A game in progress](Images/MJ_6.png)

---

![Tutorial screen](Images/MJ_2.png)

## Requirements:
- `Python 3.6`
- `Flask`
  - `Flask-Socketio`
  - `Flask-Login`
  - `Flask-SQLAlchemy`
- `NumPy`

## TODO:
- Other players' tiles not displaying properly after set event
- Implement 'addgong' check to every turn  *(added, needs testing)*
    - Current 'addgong' dialogue lingers after win event, need to reset
- Handle win events:
  - ~~(calculate points for winner)~~
  - ~~*Show winning points on client side~~
  - Add overall point/score tally
- Add indicators for actions taken
- Logic to handle running out of tiles *(added, needs testing)*
- Add flowers
- Add screenshots to readme
