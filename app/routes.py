from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app import app, db, gameRoom, socketio
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import join_room, leave_room, emit
from app.models import User
from werkzeug.urls import url_parse


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory('media', filename)


@app.route('/')
@app.route('/index')
@login_required
def index():
    inRoom = None
    if current_user.username in gameRoom.activePlayers:
        rC = gameRoom.roomContent
        inRoom = [rID for rID in gameRoom.rooms if current_user.username in rC[rID]['players']][0]
    return(render_template("index.html", title='Home Page', inRoom=inRoom))


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
    if current_user.username in gameRoom.activePlayers:
        flash('you are already in a room')
        return(redirect(url_for('index')))
    try:
        roomID = gameRoom.createRoom(current_user.username)
    except ValueError:
        flash('too many rooms active')
    return(redirect(url_for('room', roomID=roomID)))


@app.route('/room/<roomID>')
@login_required
def room(roomID):
    roomID = roomID.upper()
    if not gameRoom.roomExists(roomID):
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if not gameRoom.playerInRoom(roomID, current_user.username):
        return(redirect(url_for('leaveRoom', roomID=roomID)))
    if gameRoom.roomContent[roomID]['playing']:
        return(redirect(url_for('game', roomID=roomID)))
    players = gameRoom.roomContent[roomID]['players']
    username = gameRoom.roomContent[roomID]['owner']
    players = [un for un in players if un != username]
    owner = (current_user.username == username)
    return render_template('lobby.html', title='lobby', players=players,
                           roomID=roomID, owner=owner, username=username)


@app.route('/room/<roomID>/join')
@login_required
def joinRoom(roomID):
    roomID = roomID.upper()
    if gameRoom.roomExists(roomID):
        try:
            gameRoom.addPlayer(roomID, current_user.username)
            socketio.emit('playerChange', room=roomID)
            return(redirect(url_for('room', roomID=roomID)))
        except (ValueError, KeyError):
            flash('player not in room')
            return(redirect(url_for('index')))
    else:
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))


@socketio.on('connected_to_lobby')
def connectLobby(roomID):
    roomID = roomID.upper()
    if current_user.is_authenticated and gameRoom.roomExists(roomID):
        if gameRoom.playerInRoom(roomID, current_user.username):
            join_room(roomID)
            gameRoom.roomContent[roomID]['sid'][current_user.username] = request.sid


@socketio.on('connected_to_game')
def connectGame(roomID):
    roomID = roomID.upper()
    if current_user.is_authenticated and gameRoom.roomExists(roomID):
        if gameRoom.playerInRoom(roomID, current_user.username):
            join_room(roomID)
            gameRoom.roomContent[roomID]['sid'][current_user.username] = request.sid
            hand = gameRoom.game(roomID).showHand(current_user.username)
            emit('initialise', (gameRoom.roomContent[roomID]['players'],
                                gameRoom.game(roomID).playerDict[current_user.username]))
            emit('showHand', list(hand))
            emit('drawDiscards', gameRoom.game(roomID).showDiscards())
            emit('drawSets', gameRoom.game(roomID).showSets())
            handSizes = gameRoom.game(roomID).handSizes(current_user.username)
            emit('drawHands', handSizes)
            try:
                player, tile, sT, sO = gameRoom.game(roomID).action()
                if player == current_user.username:
                    playerSid = gameRoom.roomContent[roomID]['sid'][player]
                    if sT == 'win':
                        socketio.emit('showWin', (tile, [sO]), room=playerSid)
                    elif len(sO) > 0:
                        socketio.emit('showChoices', (tile, sT, sO), room=playerSid)
            except(ValueError, TypeError, AttributeError):
                return


@socketio.on('discardTile')
def discardTile(tile, roomID):
    player = current_user.username
    if current_user.is_authenticated and gameRoom.roomExists(roomID) and\
            gameRoom.playerInRoom(roomID, player):
        try:
            player, tile, sT, sO = gameRoom.game(roomID).discard(tile, player)
        except(TypeError, ValueError):
            return
        hand = gameRoom.game(roomID).showHand(current_user.username)
        emit('showHand', list(hand))
        socketio.emit('discardTileHand', current_user.username, room=roomID)
        playerSid = gameRoom.roomContent[roomID]['sid'][player]
        if sT == 'win':
            socketio.emit('showWin', (tile, [sO]), room=playerSid)
        elif len(sO) > 0:
            socketio.emit('showChoices', (tile, sT, sO), room=playerSid)
        else:
            loc = sT
            socketio.emit('discardTileDisp', (tile, player, loc), room=roomID)
            draw(roomID)


@socketio.on('winChoice')
def winChoice(roomID, winInd):
    player = current_user.username
    if current_user.is_authenticated and gameRoom.roomExists(roomID) and\
            gameRoom.playerInRoom(roomID, player):
        try:
            player, tile, sT, sO = gameRoom.game(roomID).playerWin(player, winInd)
        except (ValueError, AttributeError):
            return
        playerSid = gameRoom.roomContent[roomID]['sid'][player]
        if winInd == 1 and sT == '':
            socketio.emit('playerWin', (player, tile, sO), room=roomID)
        elif sT == 'win':
            socketio.emit('showWin', (tile, [sO]), room=playerSid)
        elif len(sO) > 0:
            socketio.emit('showChoices', (tile, sT, sO), room=playerSid)
        else:
            loc = sT
            socketio.emit('discardTileDisp', (tile, player, loc), room=roomID)
            draw(roomID)


@socketio.on('optChoice')
def optChoice(roomID, setInd):
    player = current_user.username
    if current_user.is_authenticated and gameRoom.roomExists(roomID) and\
            gameRoom.playerInRoom(roomID, player):
        try:
            player, tile, sT, sO = gameRoom.game(roomID).act(player, setInd)
        except IndexError:
            return
        if setInd == 0 and len(sO) == 0:
            loc = sT
            socketio.emit('discardTileDisp', (tile, player, loc), room=roomID)
            draw(roomID)
        elif setInd == 0:
            playerSid = gameRoom.roomContent[roomID]['sid'][player]
            socketio.emit('showChoices', (tile, sT, sO), room=playerSid)
        else:
            loc, newSet = sT, sO
            if len(newSet) == 4:
                draw(roomID)
                # draw
                pass
            socketio.emit('addSet', (player, loc, newSet), room=roomID)
            hand = gameRoom.game(roomID).showHand(current_user.username)
            emit('showHand', list(hand))
            handSize = len(hand)
            socketio.emit('oneHand', (player, handSize), room=roomID)


def draw(roomID):
    tile, player, winBool = gameRoom.game(roomID).draw()
    playerSid = gameRoom.roomContent[roomID]['sid'][player]
    socketio.emit('playerDraw', tile, room=playerSid)
    socketio.emit('blindDraw', player, room=playerSid)
    if winBool:
        hand = gameRoom.game(roomID).showHand(current_user.username)[:-1]
        socketio.emit('showWin', (tile, [hand]), room=playerSid)


@socketio.on('leave')
def leaveLobby(roomID):
    if current_user.is_authenticated:
        leave_room(roomID)


@app.route('/room/<roomID>/leave')
@login_required
def leaveRoom(roomID):
    roomID = roomID.upper()
    if not gameRoom.roomExists(roomID):
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if not gameRoom.playerInRoom(roomID, current_user.username):
        flash('you are not in room {}'.format(roomID))
        return(redirect(url_for('index')))
    try:
        if gameRoom.roomOwner(roomID, current_user.username):
            return(redirect(url_for('closeRoom', roomID=roomID)))
        sid = gameRoom.roomContent[roomID]['sid'][current_user.username]
        socketio.emit('leaveRoom', room=sid)
        gameRoom.removePlayer(roomID, current_user.username)
        socketio.emit('playerChange',  room=roomID)
        return(redirect(url_for('index')))
    except (ValueError, KeyError):
        return(redirect(url_for('index')))


@app.route('/room/<roomID>/remove/<username>')
@login_required
def removePlayer(roomID, username):
    roomID = roomID.upper()
    if not gameRoom.roomExists(roomID):
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if not gameRoom.playerInRoom(roomID, username):
        flash('player {} is not in room {}'.format(username, roomID))
        return(redirect(url_for('index')))
    try:
        if gameRoom.roomOwner(roomID, current_user.username):
            sid = gameRoom.roomContent[roomID]['sid'][username]
            gameRoom.removePlayer(roomID, username)
            socketio.emit('leaveRoom', roomID, room=sid)
            socketio.emit('playerChange', room=roomID)
        return(redirect(url_for('room', roomID=roomID)))
    except (ValueError):
        flash('player not in room'.format(roomID))
        return(redirect(url_for('index')))
    except KeyError:
        return(redirect(url_for('index')))


@app.route('/room/<roomID>/close')
@login_required
def closeRoom(roomID):
    roomID = roomID.upper()
    if not gameRoom.roomExists(roomID):
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if not gameRoom.roomOwner(roomID, current_user.username):
        flash('you are not the owner of room {}'.format(roomID))
        return(redirect(url_for('room', roomID=roomID)))
    gameRoom.closeRoom(roomID)
    flash('room {} is closed'.format(roomID))
    socketio.emit('playerChange', room=roomID)
    socketio.close_room(roomID)
    return(redirect(url_for('index')))


@app.route('/room/<roomID>/start')
@login_required
def startGame(roomID):
    roomID = roomID.upper()
    if not gameRoom.roomExists(roomID):
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if not gameRoom.roomOwner(roomID, current_user.username):
        flash('you are not the owner of room {}'.format(roomID))
        return(redirect(url_for('room', roomID=roomID)))
    try:
        gameRoom.startGame(roomID)
        socketio.emit('playerChange', room=roomID)
        return(redirect(url_for('room', roomID=roomID)))
    except ValueError:
        flash('room is not full yet')
        return(redirect(url_for('room', roomID=roomID)))


@app.route('/room/<roomID>/game')
@login_required
def game(roomID):
    roomID = roomID.upper()
    if not gameRoom.roomExists(roomID):
        flash('room {} does not exist'.format(roomID))
        return(redirect(url_for('index')))
    if not gameRoom.roomContent[roomID]['playing']:
        flash('game not active yet'.format(roomID))
        return(redirect(url_for('room', roomID=roomID)))
    owner = (current_user.username == gameRoom.roomContent[roomID]['owner'])
    return render_template('game.html', title='game', owner=owner, roomID=roomID)
