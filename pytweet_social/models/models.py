from pytweet_social.database import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from copy import copy

# EXERCISE: Implement association table that holds Favorite information　=========================
#pytweet_id, user_id, favorite_association
favorite_association_table = db.Table('favorite_association', db.Model.metadata,
                             db.Column('pytweet_id', db.Integer, db.ForeignKey('pytweets.id')),
                             db.Column('user_id', db.Integer, db.ForeignKey('users.id')))
# ====================================================================================

# EXERCISE: Let's create a Friendship table representing Follow relationship =============================
following_association_table = db.Table('following_associations', db.Model.metadata,
                              db.Column('source_user_id', db.Integer, db.ForeignKey('users.id'), index=True),
                              db.Column('target_user_id', db.Integer, db.ForeignKey('users.id'), index=True),
                              db.UniqueConstraint('source_user_id', 'target_user_id', name='unique_follow')
                              )
# ====================================================================================
retweet_association_table = db.Table('retweet_association', db.Model.metadata,
                            db.Column('user_id', db.Integer, db.ForeignKey('users.id'), index=True),
                            db.Column('pytweet_id', db.Integer, db.ForeignKey('pytweets.id'), index=True),
                            db.Column('comment', db.Text, nullable=True),
                            db.Column('created_at', db.DateTime, nullable=False, default=func.now()),
                            db.Column('updated_at', db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
                            )
favorite_comment_association_table = db.Table('favorite_comment_association', db.Model.metadata,
                                    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id')),
                                    db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    screen_name = db.Column(db.String(21), unique=True)
    firstname = db.Column(db.String(20), unique=True)
    lastname = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(80))
    auth_status = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text(240))
    avatar_url = db.Column(db.Text(500))    # Hold only URL of uploading avatar

    # EXERCISE: Implement relations using back_populates instead of backref =========
    pytweets = db.relationship("Pytweet", order_by="desc(Pytweet.updated_at)", back_populates='user')
    # ======================================================================

    liked_pytweets = db.relationship("Pytweet", back_populates="likers")


    # EXERCISE: Let's add a self-reference relation to get the list of people who are following ====
    followings = db.relationship("User",
                                secondary=following_association_table,
                                primaryjoin=(id == following_association_table.c.source_user_id),
                                secondaryjoin=(id == following_association_table.c.target_user_id),
                                backref=db.backref('following_association_table')
                                )
    # ==============================================================================================
    retweeted_pytweets = db.relationship("Pytweet", back_populates="retweets")

    user_comments = db.relationship("Comment", back_populates="commenters")

    comment_liked = db.relationship("Comment", back_populates="comment_likers")

    user_subcomments = db.relationship("SubComment", back_populates="subcommenters")

    def __init__(self, screen_name, email, password):
        self.screen_name = screen_name
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.screen_name)

    @staticmethod
    def search_by_keyword(keyword):
        # SELECT * FROM users WHERE screen_name LIKE '%keyword%'
        search = db.session.query(User).filter(User.screen_name.like('%\\' + keyword + '%', escape='\\')).all()
        return search

    #follow user
    def follow(self, target):
        if target not in self.followings:
            self.followings.append(target)
    
    #unfollow user
    def un_follow(self, target):
        if target in self.followings:
            self.followings.remove(target)

    def was_followed_by(self, source):
        return self in source.followings

    #display the tweets of the users we follow
    def timeline_targets(self):
        _followings = copy(self.followings)
        _followings.append(self)
        return _followings
    
    def following_count(self, source):
        # SELECT COUNT(*) FROM following_association WHERE source_user_id=source
        return db.session.query(following_association_table).filter(following_association_table.c.source_user_id==source).count()

    def followers_count(self, source):
        return db.session.query(following_association_table).filter(following_association_table.c.target_user_id==source).count()
    
class Pytweet(db.Model):
    __tablename__ = 'pytweets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text(255))
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # EXERCISE: Implement the relation by using back_populates as belonging to User =======
    user = db.relationship("User", back_populates='pytweets')
    # ===================================================================================

    likers = db.relationship("User", secondary=favorite_association_table, back_populates="liked_pytweets")

    retweets = db.relationship("User", secondary=retweet_association_table, back_populates="retweeted_pytweets")

    comments = db.relationship("Comment", back_populates="pytweet")

    # Here is a method to make it easier to read Pytweet's problems caused in an error console
    def __repr__(self):
        return '<Pytweet id={id} body={body!r}>'.format(
            id=self.id, body=self.body)

    def liked_by(self, user):
        return user in self.likers

    @staticmethod
    def likes(pytweet_id):
        likes_total = db.session.query(favorite_association_table).filter(favorite_association_table.c.pytweet_id == pytweet_id).count()
        return likes_total

    #####################################################################
    def retweeted_by(self, user):
        return user in self.retweets

    @staticmethod
    def retweet_count(pytweet_id):
        retweets_total = db.session.query(retweet_association_table).filter(retweet_association_table.c.pytweet_id == pytweet_id).count()
        return retweets_total
    #####################################################################


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    pytweet_id = db.Column(db.Integer, db.ForeignKey('pytweets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())

    pytweet = db.relationship('Pytweet', back_populates="comments")

    commenters = db.relationship('User', back_populates="user_comments")

    comment_likers = db.relationship('User', secondary=favorite_comment_association_table , back_populates="comment_liked")

    subcomments = db.relationship('SubComment', back_populates="comment")

    def comment_liked_by(self, user):
        return user in self.comment_likers

    @staticmethod
    def comment_likes(comment_id):
        comment_likes_total = db.session.query(favorite_comment_association_table).filter(favorite_comment_association_table.c.comment_id == comment_id).count()
        return comment_likes_total

class SubComment(db.Model):
    __tablename__ = 'subcomments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    subcomment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())

    comment = db.relationship('Comment', back_populates="subcomments")
    
    subcommenters = db.relationship('User', back_populates="user_subcomments")
