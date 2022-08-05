#!/usr/bin/env python3

# internal libraries
from typing import Optional

# external libraries
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy_utils.functions import database_exists
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.fields import EmailField  # wtforms version 3
from wtforms.validators import DataRequired, Email

# app library imports
from database import (db, add_book, has_book, get_books, get_book, set_book_editable,
                      delete_book, is_book_editable, get_book_title)


app = Flask(__name__)


app.config['SECRET_KEY'] = 'InOrderToHaveFormsIHaveToUseASecretKey!'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def lt_render_template(template_name_or_list, **context) -> str:
    """custom render function to add variables need for the top navigation bar."""
    if context is None:
        context = {}
    # this variable is needed for the nav bar
    context['_books'] = get_books()

    return render_template(template_name_or_list, **context)


@app.route('/')
def index():
    return lt_render_template('index.html')


# Function that returns snippets for search.
# NOTE: This prioritizes the first match of most importance, not a "best" match per say.
# * Link is not created, just need to figure out the article's number, shouldn't this 
# enumeration be stored in the database. Store b_id.
# * Can HTML be passed to jinja for links?
# the links can be mostly built like it is built in the article.html
# * NOTE: As written, this function will have to be configured per book.
# don't worry about length
# * MongoDB's text search seems smart enough to pickup words that are similar
#   so a search for 'declaration' also result in 'declaring' and other similar
#   words.  More code would be needed on this end to properly deal with that.
# TODO: Return needs to be a dictionary. 
def search_snippet(rec, query: str, snippet_length:int=400) -> Optional[dict]:
    """create a string snippet from a search record"""
    # do some preprocessing on results to create snippets of text search results
    # prioritize titles
    result = {}
    if query.lower() in rec['title'].lower():
        result['title'] = rec['title']
        result['art_number'] = rec['number']
        return result
    
    # print(f'rec.keys(): {rec.keys()}')
    # print(f'rec' {rec})

    # look at the articles/amendments for their subtitles
    for art in rec['legal']:
        # print(f"type(section) {type(section)}")
        # print(f"art {art}")
        # print(f'rec.keys(): {rec.keys()}')
        # print(f'isinstance(art, dict): {isinstance(art, dict)}')
        if isinstance(art, dict) and query.lower() in art['subtitle'].lower():
#            return f"{art['subtype']} {art['number']} - {art['subtitle']}"
            result['title'] = f"{art['subtype']} {art['number']} - {art['subtitle']}"
            result['art_number'] = rec['number']
            result['fragment'] = f"{art['subtype']}_{art['number']}"
            return result

    # look for a match in the contents
    for art in rec['legal']:
        # section is a list of strings
        for section in art['content']:
            # for para in section:
            # print(type(section))
                # if 'declaration' in para.lower():
                #    print('MATCH')
            if query.lower() in section.lower():
                # print(f"query: {query}\n section {section}")
                # return f"{art['subtype']} {art['number']} - {art['subtitle']}<br>" + section
                half_snip = (snippet_length - len(query)) // 2
                idx = section.find(query.lower())
                # print(f"idx: {idx}")
                if idx - half_snip < 0:
                    b_idx = 0
                else:
                    b_idx = idx - half_snip
                t_idx = idx + len(query) + half_snip
                
#                return  f"{art['subtype']} {art['number']} - {art['subtitle']}<br>" + \
#                        f"…{section[b_idx:t_idx]}…"
                result['title'] = f"{art['subtype']} {art['number']} - {art['subtitle']}"
                result['art_number'] = rec['number']
                result['fragment'] = f"{art['subtype']}_{art['number']}"

                # add ellipsis … when not at the beginning or end of the section
                result['context'] = ''
                if b_idx != 0:
                    result['context'] += '…'
                result['context'] += f"…{section[b_idx:t_idx]}"
                if t_idx != len(section):
                    result['context'] += '…'

                return result

    # fallthrough, return nothing
    return None

# TODO: need some way to create a link to the content.
# Perhaps use javascript to do keyword highlighting?
@app.route('/search/<doc_id>')
def search(doc_id=None):   
    if doc_id is None or not has_book(doc_id):
        return "Sorry, I had a problem finding that legal text."

    query = request.args.get("query")
    # mongodb does good first level of search results
    cursor = db[doc_id].find({'$text': {'$search': query}})
    results = list(cursor)

    # ensure that this database has an index 
    db[doc_id].create_index([('$**', 'text')])

    # create snippets from search results, removing results that are None values
    sch_results = list(filter(lambda x: x is not None, 
                            map(lambda r: search_snippet(r,query), results)))
#    snip_results = list(map(lambda r: search_snippet(r,query), results))
    num_results = len(sch_results)
    return lt_render_template('search_results.html', query=query, 
                                sch_results=sch_results, num_results=num_results,
                                doc_id=doc_id)


@app.route('/settings')
def settings():
    if not session['username']:
        flash('You have to be logged in to do this.')
        return redirect(url_for('login'))

    return render_template('settings.html', books=get_books(), \
            is_book_editable=is_book_editable)


@app.route('/set_tgl_bk_editable/<collection>')
def set_tgl_bk_editable(collection):
    if not session['username']:
        flash('You have to be logged in to do this.')
        return redirect(url_for('login'))

    flash(f"toggled collection '{collection}' editability")
    set_book_editable(collection)
    return render_template('settings.html', books=get_books())


class NewBookForm(FlaskForm):
   title = StringField("Title", validators=[DataRequired()])
   collection = StringField("Collection", 
                            validators=[DataRequired()])
   submit = SubmitField('Add Book')

@app.route('/new_book', methods=['GET', 'POST'])
def new_book():
    if not session['username']:
        flash('You have to be logged in to do this.')
        return redirect(url_for('login'))

    newbook_form = NewBookForm()
    if newbook_form.validate_on_submit():
        title = newbook_form.title.data
        collection = newbook_form.collection.data
        success = add_book(collection, title)
        if success:
            flash(f'Added book: {title}')
        else:
            flash('Failed to add book.')
    
    return lt_render_template('new_book.html', newbook_form=newbook_form)


class DeleteBookForm(FlaskForm):
    complete_delete = BooleanField('Completely Delete Book from Database?')
    submit = SubmitField('Delete Book')

@app.route('/set_delete_book/<collection>', methods=['GET', 'POST'])
def set_delete_book(collection):
    if not session['username']:
        flash('You have to be logged in to do this.')
        return redirect(url_for('login'))

    del_form = DeleteBookForm()
    print(f'is_book_editable(collection): {is_book_editable(collection) }')
    if not is_book_editable(collection):
        flash(f'Cannot deleted "{collection}", not editable.  Go to settings to make editable.')
        return redirect(url_for('settings'))

    if del_form.validate_on_submit():
        delete_book(collection)
        flash(f'Deleted "{collection}"')
        if del_form.complete_delete.data:
            print("TODO: Completely delete the collection from the database.")
        
        return redirect(url_for('settings'))
    # else:
        # message = f'Cannot deleted "{collection}", not editable.  Go to settings to make editable.'
    # TODO retrieve the book for bk    
    return lt_render_template('delete_book.html', bk=get_book(collection), del_form=del_form)


# for browsing an article
@app.route('/browse/<doc_id>/<b_id>')
def browse(doc_id=None, b_id=0):
    """browse an article of legal text"""
    def get_article_names_enumerated(db):
        articles = db[doc_id].find()
        article_names = map(lambda a: a['title'], articles)
        return enumerate(article_names)

#    print(f"DOC: {doc_id}, B_ID: {b_id}")
#   print(f"doc not in db_collection {doc not in db_collection}")
    if doc_id is None or b_id is None or not has_book(doc_id):
        return "Sorry, I had a problem finding that legal text"
    
    # db[doc_id]

    articles = db[doc_id].find()
#    article_names = list(map(lambda a: list(a.keys())[1], articles))
    article_names = tuple(map(lambda a: a['title'], articles))
    # redo because map modifies the state of articles
    articles = db[doc_id].find()
    legals = tuple(map(lambda a: a['legal'], articles))
#    print(f'len(article_names): {len(article_names)}')
#    print(f'len(legals): {len(legals)}')
    # TODO: Should I protect for an IndexError
    try:
        article_name = article_names[int(b_id)]
    except IndexError as err:
        flash(f'This legal text does not have that many articles.  (IndexError: {err})')
        return redirect(url_for('index'))

    legal = legals[int(b_id)]
#    print(article_name)
#   
#    print(legal)
    # article_name = list(article.keys())[1]
    # return article[article_name]
    # return render_template()
    # art_legal is a list of dictionaries representing the section text.
    return lt_render_template('article.html', article_name=article_name, art_legal=legal, 
                            articles=get_article_names_enumerated(db), doc_id=doc_id,
                            title=get_book_title(doc_id))

class EditForm(FlaskForm):
    content = TextAreaField()
    submit = SubmitField('Save')


@app.route('/edit/<collection>', methods=['GET', 'POST'])
def edit(collection):
    edit_form = EditForm()
    # convert the JSON to markdown
    # edit_form.content.data = converted_md
    edit_form.content.data = 'THIS FEATURE DOES NOT WORK.'
    if edit_form.validate_on_submit():
        # convert the markdown to JSON
        # save results to the database
        pass

    return lt_render_template('edit.html', edit_form=edit_form, 
                               title=get_book_title(collection))

############## REGISTRATION AND LOGIN CODE ##########################

user_db = SQLAlchemy(app)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()]) 
    submit = SubmitField('Login')

# this is a login form
@app.route('/login', methods=['GET', 'POST'])
def login() -> str:
    if 'username' in session and session['username']:
        # return render_template('secretPage.html')
        return redirect(url_for('index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        # print('login_form submittal')
        username = login_form.username.data
        password = login_form.password.data
        users = User.query.filter(User.username == username).all()

        if users == []:
            flash('Could not login, that username does not seem to exist.')
        elif users[0].password == password:
            session['username'] = username
            flash(f'{username} is now logged in.')
#            return render_template('secretPage.html')
            return redirect(url_for('index'))

    return lt_render_template('login/login.html', login_form=login_form)



class RegisterForm(FlaskForm):
    first = StringField("First", validators=[DataRequired()])
    last = StringField("Last", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired()])
    confirm_password = StringField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField('Register Now')


class User(user_db.Model):
    __tablename__ = 'user'
    id = user_db.Column(user_db.Integer, primary_key = True)
    first = user_db.Column(user_db.Text)
    last = user_db.Column(user_db.Text)
    username = user_db.Column(user_db.Text)
    email = user_db.Column(user_db.Text)
    password = user_db.Column(user_db.Text)

    def __init__(self, first, last, username, email, password):
        self.first = first
        self.last = last
        self.username = username
        self.email = email
        self.password = password
    
    def __repr__(self):
        return f'User: {self.username}'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = RegisterForm()

    if signup_form.validate_on_submit():
#        print("signup_form.validate_on_submit() ran")
        email = signup_form.email.data
        password = signup_form.password.data
        confirm_password = signup_form.confirm_password.data
        username = signup_form.username.data

        email_exists = User.query.filter(User.email == email).all()
        username_exists = User.query.filter(User.username == username).all()

        if password != confirm_password:
            flash("There's a problem. The passwords you entered are not the same.")
            signup_form.password.data = ''
            signup_form.confirm_password.data = ''
        # Check if the email address is already in the database.
        elif len(email_exists) > 0:
            flash(f"There's a problem. Another user is already using the email address: '{email}'.  I cannot create this account. Sorry.")
        # Check if username already exists.
        elif len(username_exists) > 0:
            flash("There's a problem. Another user already has that username. Sorry.")
        else:
            first = signup_form.first.data
            last = signup_form.last.data

            new_user = User(first, last, username, email, password)
            user_db.session.add(new_user)
            user_db.session.commit()

            return render_template('login/thankyou.html')

    return render_template('login/signup.html', signup_form=signup_form)

@app.route('/logout')
def logout():
    session['username'] = ''
    flash('User is now logged out.')
    return redirect(url_for('index'))

def init_user_db() -> bool:
    """Initialize the user database, returns True - created the database, False - database already exists"""
    if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
        print('Creating the database.')
        user_db.create_all()
        # add something to the database so that the user table will be created
        dummy_user = User('DUMMY', 'USER', '-', 'dummy@user.org', 'LONGPASSWORDFORADummyUser')
        user_db.session.add(dummy_user)
        user_db.session.commit()
        return True
    return False

# Check for the user database's existence, if it doesn't exist create the database.
# This is intentionally initialized so that init_db() is defined and ran before __main__.
init_user_db()

####### END OF REGISTRATION AND LOGIN CODE ##########################


if __name__ == '__main__':
    import os
#    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
