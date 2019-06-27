from flask import request, redirect, url_for, render_template, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from pytweet_social import app, db
from pytweet_social.models import Pytweet, User, Comment, SubComment
from urllib.request import Request, urlopen
import json
import base64

bootstrap = Bootstrap(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class LoginForm(FlaskForm):
    screen_name = StringField('username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    screen_name = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class PytweetForm(FlaskForm):
    body = StringField('body', validators=[InputRequired(), Length(min=1, max=144)])


class UserSearchForm(FlaskForm):
    keyword = StringField('keyword', validators=[Length(min=1, max=20)])


def img_upload_to_imgur(img_data):
    # Define header to send a request
    header = {'Authorization': 'Client-ID {}'.format(app.config['IMGUR_CLI_ID']),
              'Content-Type': 'application/json'}
    data = {'image': img_data}                          # Define the data to send
    encoded_data = json.dumps(data).encode('utf-8')     # Encode the data to send with urllib

    # Actually send a request
    req = Request(app.config["IMG_UPLOAD_URL"], encoded_data, headers=header)
    #  Pick up the image of link by opening response
    with urlopen(req) as res:
        body = json.loads(res.read().decode('utf8'))
    return body['data']['link']


def convert_file_to_data(file_obj):
    _raw_binary = file_obj.read()
    _encoded_bin = base64.b64encode(_raw_binary).decode('utf-8')
    return _encoded_bin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return redirect(url_for('timeline'))


@app.route('/users/tmp/upload_dir/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_DIR'], filename)


@app.route('/tmp/upload_dir/<path:filename>')
def uploaded_file_main(filename):
    return send_from_directory(app.config['UPLOAD_DIR'], filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(screen_name=form.screen_name.data).first()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    return redirect('/timeline')
                else:
                    flash('Invalid Password')
            else:
                flash('Invalid screen_name or password')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(screen_name=form.screen_name.data,
                        email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('New User was successfully created')
        return redirect('/timeline')
    return render_template('register.html', form=form)


@app.route('/users/me')
@login_required
def show_me():
    return render_template('user/show.html', user=current_user)


@app.route('/users/me/edit', methods=['GET', 'POST'])
@login_required
def edit_me():
    if request.method == 'POST':
        current_user.screen_name = request.form['screen_name']
        current_user.email = request.form['email']
        current_user.bio = request.form['bio']
        if 'avatar' in request.files:
            avatar = request.files['avatar']  # Get the object called FileStorage
            avatar_data = convert_file_to_data(avatar)
            avatar_url = img_upload_to_imgur(avatar_data)  # Get the link by uploading

            current_user.avatar_url = avatar_url
        db.session.commit()
        return redirect(url_for('show_me'))
    return render_template('user/edit.html', user=current_user)


@app.route('/users/me/delete', methods=['POST'])
@login_required
def delete_me():
    db.session.delete(current_user)
    db.session.commit()
    flash('Your data was successfully deleted')
    return redirect('login')


@app.route('/users/<int:user_id>')
@login_required
def show_user(user_id):
    user = User.query.get(user_id)
    return render_template('user/show.html', user=user)


@app.route('/users/<int:target_user_id>/friendship', methods=['POST', 'DELETE'])
@login_required
def handle_friendship(target_user_id):
    target_user = User.query.get(target_user_id)

    if target_user is None:
        return __error_not_found()

    if request.method == 'POST':
        if target_user.was_followed_by(current_user):
            # When you already followed, write the program the following
            return __error_bad_request()
        current_user.follow(target_user)
        db.session.commit()
        return __success_ok()
    elif request.method == 'DELETE':
        if not target_user.was_followed_by(current_user):
            # When you do not follow yet, of course, you can't cancel
            return __error_bad_request()
        current_user.un_follow(target_user)
        db.session.commit()
        return __success_ok()
    else:
        return __error_bad_request()


@app.route('/users/search', methods=['POST', 'GET'])
@login_required
def search_user():
    form = UserSearchForm()

    if request.method == 'POST':

        if form.validate_on_submit():
            _key = form.keyword.data
            results = User.search_by_keyword(_key)

            return render_template('user/search.html',
                                   form=form,
                                   results=results,
                                   current_user=current_user)

    return render_template('user/search.html', form=form)

@app.route('/user/<int:user_id>/profile')
@login_required
def user_profile(user_id):
    user = User.query.get(user_id)
    pytweets = Pytweet.query.get(user_id)
    return render_template('user/show.html', user=user, pytweets=pytweets)


@app.route('/timeline', methods=['POST', 'GET'])
@login_required
def timeline():
    # EXERCISE: Implementation to get the pytweets you want to display on the timeline ===========
    tweets_total = Pytweet.query.filter_by(user_id=current_user.id).count()
    targets = current_user.timeline_targets()
    pytweets = []
    for user in targets:
        for pytweet in user.pytweets:
            pytweets.append(pytweet)
    # ================================================================
    form = PytweetForm()
    following = current_user.following_count(current_user.id)
    followers = current_user.followers_count(current_user.id)
    if request.method == 'POST':
        if form.validate_on_submit():
            pytweet = Pytweet(user=current_user,
                              body=form.body.data)
            db.session.add(pytweet)
            db.session.commit()
            form.body.data = ''
            flash('New Pytweet was successfully posted')
            return redirect(url_for('timeline'))

    return render_template('timeline.html', pytweets=pytweets, form=form, following=following, followers=followers, tweets_total=tweets_total)


@app.route('/pytweets')
@login_required
def list_pytweets():
    pytweets = Pytweet.query.order_by(Pytweet.id.desc()).all()
    return render_template('pytweet/list.html', pytweets=pytweets)


@app.route('/pytweets/<int:pytweet_id>/')
@login_required
def show_pytweet(pytweet_id):
    pytweet = Pytweet.query.get(pytweet_id)
    return render_template('pytweet/show.html', pytweet=pytweet)


@app.route('/pytweets/new/', methods=['GET', 'POST'])
@login_required
def create_pytweet():
    if request.method == 'POST':
        form = PytweetForm()

        if form.validate_on_submit():
            pytweet = Pytweet(user=current_user,
                              body=form.body.data)
            db.session.add(pytweet)
            db.session.commit()
            flash('New Pytweet was successfully posted')
            return redirect(url_for('list_pytweets'))

    return render_template('pytweet/edit.html')


@app.route('/pytweets/<int:pytweet_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_pytweet(pytweet_id):
    pytweet = Pytweet.query.get(pytweet_id)
    form = PytweetForm()

    if pytweet is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response

    if request.method == 'POST':

        if form.validate_on_submit():
            pytweet.body = form.body.data
            db.session.commit()
            return redirect(url_for('timeline'))
    else:
        form.body.data = pytweet.body

    return render_template('pytweet/edit.html', pytweet=pytweet, form=form)


@app.route('/pytweet/<int:pytweet_id>/delete/', methods=['POST'])
@login_required
def delete_pytweet(pytweet_id):
    pytweet = Pytweet.query.get(pytweet_id)

    if pytweet is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response

    db.session.delete(pytweet)
    db.session.commit()
    flash('The pytweet was successfully deleted')
    return redirect(url_for('timeline'))

@app.route('/pytweet/<int:pytweet_id>/favorite', methods=['POST', 'DELETE'])
def like_pytweet(pytweet_id):
    pytweet = Pytweet.query.get(pytweet_id)

    if request is None:
        return __error_not_found()
    
    if request.method == "POST":
        if current_user in pytweet.likers:
            return __error_bad_request()
        pytweet.likers.append(current_user)
        db.session.commit()
        likes = pytweet.likes(pytweet_id)
        return str(likes)

    if request.method == "DELETE":
        if current_user not in pytweet.likers:
            return __error_bad_request()
        pytweet.likers.remove(current_user)
        db.session.commit()
        likes = pytweet.likes(pytweet_id)
        return str(likes)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


def __error_not_found():
    response = jsonify({'status': 'Not Found'})
    response.status_code = 404
    return response


def __error_bad_request():
    response = jsonify({'status': 'Bad Request'})
    response.status_code = 400
    return response


def __success_ok():
    response = jsonify({'status': 'ok'})
    response.status_code = 200
    return response


@app.route('/<screen_name>/<int:user_id>/profile', methods=['POST', 'GET'])
@login_required
def show_profile(user_id, screen_name):
    tweets_total = Pytweet.query.filter_by(user_id=user_id).count()
    pytweets = Pytweet.query.filter_by(user_id=user_id).all()
    user = User.query.get(user_id)
    following = user.following_count(user.id)
    followers = user.followers_count(user.id)
    return render_template('user/profile.html', pytweets=pytweets, following=following, followers=followers, tweets_total=tweets_total, user=user)


@app.route('/pytweet/<int:pytweet_id>/retweet', methods=['POST', 'DELETE'])
def retweet_pytweet(pytweet_id):
    pytweet = Pytweet.query.get(pytweet_id)

    if request is None:
        return __error_not_found()
    
    if request.method == "POST":
        if current_user in pytweet.retweets:
            return __error_bad_request()
        pytweet.retweets.append(current_user)
        db.session.commit()
        retweets = pytweet.retweet_count(pytweet_id)
        return str(retweets)

    if request.method == "DELETE":
        if current_user not in pytweet.retweets:
            return __error_bad_request()
        pytweet.retweets.remove(current_user)
        db.session.commit()
        retweets = pytweet.retweet_count(pytweet_id)
        return str(retweets)

@app.route('/pytweets/<int:pytweet_id>/comment/', methods=['POST', 'GET'])
@login_required
def show_comment(pytweet_id):
    pytweet = Pytweet.query.get(pytweet_id)
    comments = Comment.query.filter_by(pytweet_id=pytweet_id).order_by(Comment.updated_at.desc()).all()
    return render_template('pytweet/comment.html', pytweet=pytweet, comments=comments)

@app.route('/<int:pytweet_id>/comment/add', methods=['GET', 'POST'])
@login_required
def new_comment(pytweet_id):
    if request.method == "POST":
        commenting = Comment(pytweet_id = pytweet_id, user_id = current_user.id, comment = request.form['comment'])
        db.session.add(commenting)
        db.session.commit()
        comments = Comment.query.filter_by(pytweet_id=pytweet_id).order_by(Comment.updated_at.desc()).all()
   
    return render_template('pytweet/comments.html', comments=comments)

@app.route('/<int:comment_id>/comment/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response

    if request.method == 'POST':
        comment.comment = request.form['new_comment']
        db.session.commit()
        comments = Comment.query.filter_by(pytweet_id=comment.pytweet_id).order_by(Comment.updated_at.desc()).all()
        return render_template('pytweet/comments.html', comments=comments)
    

        








@app.route('/comment/<int:comment_id>/favorite', methods=['POST', 'DELETE'])
def like_comment(comment_id):
    comment = Comment.query.get(comment_id)

    if request is None:
        return __error_not_found()
    
    if request.method == "POST":
        if current_user in comment.comment_likers:
            return __error_bad_request()
        comment.comment_likers.append(current_user)
        db.session.commit()
        comment_likes = comment.comment_likes(comment_id)
        return str(comment_likes)

    if request.method == "DELETE":
        if current_user not in comment.comment_likers:
            return __error_bad_request()
        comment.comment_likers.remove(current_user)
        db.session.commit()
        comment_likes = comment.comment_likes(comment_id)
        return str(comment_likes)

@app.route('/<int:comment_id>/subcomment/add', methods=['GET', 'POST'])
@login_required
def new_subcomment(comment_id):
    if request.method == "POST":
        subcommenting = SubComment(comment_id = comment_id, user_id = current_user.id, subcomment = request.form['subcomment'])
        db.session.add(subcommenting)
        db.session.commit()
        subcomments = SubComment.query.filter_by(comment_id=comment_id).order_by(SubComment.updated_at.desc()).all()
        return render_template('pytweet/subcomments.html', subcomments=subcomments)

@app.route('/subcomments/<int:subcomment_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_subcomment(subcomment_id):
    subcomment = SubComment.query.get(subcomment_id)

    if subcomment is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response

    if request.method == 'POST':

        SubComment.subcomment = request.form['subcomment']
        db.session.commit()
        return render_template('comments.html')

#show subcomments
@app.route('/comments/<int:comment_id>/sub/', methods=['GET', 'POST'])
@login_required
def show_sub_comments(comment_id):
    subcomments = SubComment.query.filter_by(comment_id=comment_id).order_by(SubComment.updated_at.desc()).all()
    return render_template("pytweet/subcomments.html", subcomments=subcomments)

