from flask import render_template, flash, redirect, url_for, request
from app import app, db, socketio
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import join_room, leave_room, emit
from app.models import User, Room
from werkzeug.urls import url_parse
from random import choices
from string import ascii_uppercase
import functools
from initGame import MJgame


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = User.query.filter_by(username=current_user.username).first()
    inRoom = user.in_room
    return(render_template("index.html", title='Home Page', inRoom=inRoom))


@app.route('/learn')
def learn():
    return(render_template("learn.html"))


@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return(redirect(url_for('index')))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # filter_by method only includes objects of matching username
        # first returns first matching result or None
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username/password combination')
            return(redirect(url_for('login')))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # url_parse function ensures next argument is not a full URL
            next_page = url_for('index')
        return(redirect(next_page))
    return render_template('login.html', form=form, title='login')


@app.route('/logout')
def logout():
    logout_user()
    return(redirect(url_for('login')))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/newRoom')
@login_required
def newRoom():
    user = User.query.filter_by(username=current_user.username).first()
    if user.in_room is not None:
        flash('you are already in a room')
        return(redirect(url_for('index')))
    rooms = Room.query.all()
    maxrooms = 10
    if len(rooms) < maxrooms:
        roomID = ''.join(choices(ascii_uppercase, k=4))
        while roomID in [room.roomID for room in rooms]:
            roomID = ''.join(choices(ascii_uppercase, k=4))
        room = Room(roomID=roomID, owner_id=user.id)
        room.players.append(user)
        user.in_room = room.roomID
        user.order = 0
        user.ready = True
        db.session.add(room)
        db.session.commit()
    return(redirect(url_for('room', roomID=roomID)))


@app.route('/room/<roomID>')
@login_required
def room(roomID):
    user = User.query.filter_by(username=current_user.username).first()
    roomID = roomID.upper()
    room = Room.query.filter_by(roomID=roomID).first()
    if room is None:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if user.in_room != roomID:
        return(redirect(url_for('leaveRoom', roomID=roomID)))
    if room.JSON_string is not None:
        return(redirect(url_for('game', roomID=roomID)))
    players_q = room.players.all()
    try:
        players = [player for player in players_q
                   if player.id != room.owner_id]
        username = [player.username for player in players_q
                    if player.id == room.owner_id][0]
    except IndexError:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    return render_template('lobby.html', title='lobby', players=players,
                           roomID=roomID, username=username, user=user)


@app.route('/room/<roomID>/join')
@login_required
def joinRoom(roomID):
    user = User.query.filter_by(username=current_user.username).first()
    inRoom = user.in_room
    if inRoom is not None:
        flash('player already room {}'.format(inRoom))
        return(redirect(url_for('room', roomID=inRoom)))
    roomID = roomID.upper()
    room = Room.query.filter_by(roomID=roomID).first()
    if room is None:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    players = room.players.all()
    if len(players) == 4:
        flash('room {} is full'.format(roomID))
        return(redirect(url_for('index')))
    user.in_room = room.id
    user.ready = False
    for i in range(1, 4):
        if i not in [player.order for player in players]:
            user.order = i
    room.players.append(user)
    db.session.commit()
    socketio.emit('playerChange', room=roomID)
    return(redirect(url_for('room', roomID=roomID)))


def authentication_required(func):
    """
    wrapper for socketio events to authenticate that:
    1. The user is logged in;
    2. The user belongs to the room it claims to be in
    """
    @functools.wraps(func)
    def wrapped(roomID, *args, **kwargs):
        roomID = roomID.upper()
        room = Room.query.filter_by(roomID=roomID).first()
        if current_user.is_authenticated and room is not None:
            user = User.query.filter_by(username=current_user.username).first()
            if user is not None and user.in_room == roomID:
                return(func(roomID, user, room, *args, **kwargs))
        socketio.disconnect()

    return(wrapped)


@socketio.on('connected_to_lobby')
@authentication_required
def connectLobby(roomID, user, room):
    join_room(roomID)
    user.player_sid = request.sid
    db.session.commit()


@socketio.on('lobby_ready')
@authentication_required
def lobbyReady(roomID, user, room, ready_bool):
    user.ready = ready_bool
    db.session.commit()
    socketio.emit('playerReady', (user.order, ready_bool), room=roomID)


@socketio.on('connected_to_game')
@authentication_required
def connectGame(roomID, user, room):
    join_room(roomID)
    user.player_sid = request.sid
    db.session.commit()
    game = MJgame(in_dict=room.load_JSON())
    players = ['', '', '', '']
    players_q = room.players.all()
    for player in players_q:
        players[player.order] = player.username
    userInd = user.order
    hand = game.showHand(userInd)
    emit('initialise', (players, (userInd-game.start) % 4,
                        game.turn, userInd, game.wind, game.tilesLeft()))
    emit('showHand', hand)
    emit('drawDiscards', game.showDiscards())
    emit('drawSets', game.showSets())
    emit('drawHands', game.handSizes(userInd))
    try:
        actDict = game.action(player_in=userInd)
        emit(actDict['message'], actDict['args'])
    except(ValueError, TypeError, AttributeError, KeyError):
        return


@socketio.on('discardTile')
@authentication_required
def discardTile(roomID, user, room, tile):
    userInd = user.order
    game = MJgame(in_dict=room.load_JSON())
    try:
        actDict = game.discard(tile, userInd)
    except ValueError:
        return
    room.set_JSON(game)
    db.session.commit()
    player = actDict['player']
    player_q = room.players.filter_by(order=player).first()
    playerSid = player_q.player_sid
    hand = game.showHand(userInd)
    emit('showHand', hand)
    socketio.emit('discardTileHand', userInd, room=roomID)
    io_room = roomID if actDict['message'] == 'discardTileDisp' else playerSid
    socketio.emit(actDict['message'], actDict['args'], room=io_room)
    if 'draw' in actDict:
        draw(actDict['draw'], roomID, room)


@socketio.on('winChoice')
@authentication_required
def winChoice(roomID, user, room, winInd):
    userInd = user.order
    game = MJgame(in_dict=room.load_JSON())
    try:
        actDict = game.playerWin(userInd, winInd)
    except(ValueError, IndexError):
        return
    room.set_JSON(game)
    db.session.commit()
    if actDict is None:
        return
    player = actDict['player']
    player_q = room.players.filter_by(order=player).first()
    playerSid = player_q.player_sid
    io_room = roomID if actDict['message'] in ('discardTileDisp', 'playerWin')\
        else playerSid
    socketio.emit(actDict['message'], actDict['args'], room=io_room)
    if 'draw' in actDict:
        draw(actDict['draw'], roomID, room)


@socketio.on('optChoice')
@authentication_required
def optChoice(roomID, user, room, setInd):
    userInd = user.order
    game = MJgame(in_dict=room.load_JSON())
    try:
        actDict = game.act(userInd, setInd)
    except(ValueError, IndexError):
        return
    room.set_JSON(game)
    db.session.commit()
    if actDict is None:
        return
    player = actDict['player']
    player_q = room.players.filter_by(order=player).first()
    playerSid = player_q.player_sid
    io_room = playerSid if actDict['message'] in ('showChoices') else roomID
    socketio.emit(actDict['message'], actDict['args'], room=io_room)
    if 'playerHand' in actDict:
        emit('showHand', actDict['playerHand'])
    if 'draw' in actDict:
        draw(actDict['draw'], roomID, room)


def draw(drawDict, roomID, room):
    if drawDict is None:
        socketio.emit('gameDraw', room=roomID)
        return
    tile = drawDict['tile']
    tilesLeft = drawDict['tilesLeft']
    player = drawDict['player']
    player_q = room.players.filter_by(order=player).first()
    playerSid = player_q.player_sid
    socketio.emit('playerDraw', tile, room=playerSid)
    socketio.emit('blindDraw', (player, tilesLeft),  room=roomID)
    for action in drawDict['actionList']:
        socketio.emit(action['message'], action['args'], room=playerSid)


@socketio.on('leave')
def leaveLobby(roomID):
    if current_user.is_authenticated:
        leave_room(roomID)


@app.route('/room/<roomID>/leave')
@login_required
def leaveRoom(roomID):
    roomID = roomID.upper()
    room = Room.query.filter_by(roomID=roomID).first()
    if room is None:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    user = User.query.filter_by(username=current_user.username).first()
    if user.in_room != roomID:
        flash('you are not in room {}'.format(roomID))
        return(redirect(url_for('index')))
    try:
        if room.owner_id == user.id:
            return(redirect(url_for('closeRoom', roomID=roomID)))
        socketio.emit('leaveRoom', room=user.player_sid)
        room.JSON_string = None
        user.in_room = None
        user.ready = None
        user.order = None
        room.players.remove(user)
        db.session.commit()
        socketio.emit('playerChange',  room=roomID)
        return(redirect(url_for('index')))
    except (ValueError, KeyError):
        return(redirect(url_for('index')))


@app.route('/room/<roomID>/remove/<username>')
@login_required
def removePlayer(roomID, username):
    roomID = roomID.upper()
    room = Room.query.filter_by(roomID=roomID).first()
    user = User.query.filter_by(username=current_user.username).first()
    if room is None:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    try:
        if room.owner_id != user.id:
            flash('you are not the owner of room {}'.format(roomID))
            return(redirect(url_for('room', roomID=roomID)))
        del_user = User.query.filter_by(username=username).first()
        if del_user is None:
            flash('player not in room'.format(roomID))
            return(redirect(url_for('index')))
        if del_user.in_room != roomID:
            flash('player {} is not in room {}'.format(username, roomID))
            return(redirect(url_for('index')))
        sid = del_user.player_sid
        del_user.in_room = None
        del_user.ready = None
        del_user.order = None
        room.JSON_string = None
        room.players.remove(del_user)
        db.session.commit()
        socketio.emit('leaveRoom', roomID, room=sid)
        socketio.emit('playerChange', room=roomID)
        return(redirect(url_for('room', roomID=roomID)))
    except KeyError:
        return(redirect(url_for('index')))


@app.route('/room/<roomID>/close')
@login_required
def closeRoom(roomID):
    roomID = roomID.upper()
    room = Room.query.filter_by(roomID=roomID).first()
    if room is None:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    user = User.query.filter_by(username=current_user.username).first()
    if room.owner_id != user.id:
        flash('you are not the owner of room {}'.format(roomID))
        return(redirect(url_for('room', roomID=roomID)))
    for player in room.players.all():
        player.in_room = None
        player.order = None
        player.ready = None
    db.session.delete(room)
    db.session.commit()
    flash('room {} is closed'.format(roomID))
    socketio.emit('playerChange', room=roomID)
    socketio.close_room(roomID)
    return(redirect(url_for('index')))


@app.route('/room/<roomID>/start')
@login_required
def startGame(roomID):
    roomID = roomID.upper()
    room = Room.query.filter_by(roomID=roomID).first()
    if room is None:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    user = User.query.filter_by(username=current_user.username).first()
    if room.owner_id != user.id:
        flash('you are not the owner of room {}'.format(roomID))
        return(redirect(url_for('room', roomID=roomID)))
    players = room.players.all()
    if room.JSON_string is not None:
        return(redirect(url_for('game', roomID=roomID)))
    if len(players) < 4:
        flash('room is not full yet')
        return(redirect(url_for('room', roomID=roomID)))
    if not all(player.ready for player in players):
        flash('not all players ready')
        return(redirect(url_for('room', roomID=roomID)))
    game = MJgame()
    room.set_JSON(game)
    db.session.commit()
    socketio.emit('playerChange', room=roomID)
    return(redirect(url_for('room', roomID=roomID)))


@app.route('/room/<roomID>/game')
@login_required
def game(roomID):
    roomID = roomID.upper()
    room = Room.query.filter_by(roomID=roomID).first()
    if room is None:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if room.JSON_string is None:
        flash('game not active yet'.format(roomID))
        return(redirect(url_for('room', roomID=roomID)))
    user = User.query.filter_by(username=current_user.username).first()
    owner = (user.id == room.owner_id)
    return render_template('game.html', title='game', owner=owner, roomID=roomID)
