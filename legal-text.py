#!/usr/bin/env python3

# external libraries
from flask import Flask, redirect, render_template, request, session, url_for
# TODO install flask_wtf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired # , Email

# app library imports
from database import db, add_book, has_book, get_books

app = Flask(__name__)


app.config['SECRET_KEY'] = 'InOrderToHaveFormsIHaveToUseASecretKey!'

def lt_render_template(template_name_or_list, **context) -> str:
    
    # this is a custom render template that adds variables that are needed for every call
    if context is None:
        context = {}
    # this variable is needed for the nav bar
    context['_books'] = get_books()

    return render_template(template_name_or_list, **context)

@app.route('/')
def index():
    return lt_render_template('index.html')

@app.route('/login')
def login():
    return "This is a placeholder for a login form."

@app.route('/search/<doc_id>')
def search(doc_id=None):
    if doc_id is None or not has_book(doc_id):
        return "Sorry, I had a problem finding that legal text."

    query = request.args.get("query")

    return f"This is plumbing for search.  What you searched for was this '{query}' from the document '{doc_id}'."


@app.route('/settings')
def settings():
    pass

class NewBookForm(FlaskForm):
   title = StringField("Title", validators=[DataRequired()])
   collection = StringField("Collection", 
                            validators=[DataRequired()])
   submit = SubmitField('Add Book')

@app.route('/new_book', methods=['GET', 'POST'])
def new_book():
    message = ''
    newbook_form = NewBookForm()
    if newbook_form.validate_on_submit():
        title = newbook_form.title.data
        collection = newbook_form.collection.data
        success = add_book(collection, title)
        if success:
            message = f'Added book: {title}'
        else:
            message = f'Failed to add book.'
    
    return lt_render_template('new_book.html', newbook_form=newbook_form, message=message)


# @app.route('/test1')
# def test1():
#    articles = db.legal_text.find()
#    article_names = map(lambda a: list(a.keys())[1], articles)
#    article_names = map(lambda a: a['title'], articles)

#    return render_template("top.html", articles=enumerate(article_names))


# for browsing an article
@app.route('/browse/<doc_id>/<b_id>')
def browse(doc_id=None, b_id=0):
    """browse an article of legal text"""
    def get_article_names_enumerated(db):
        articles = db[doc_id].find()
        article_names = map(lambda a: a['title'], articles)
        return enumerate(article_names)

    print(f"DOC: {doc_id}, B_ID: {b_id}")
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
    print(f'len(article_names): {len(article_names)}')
    print(f'len(legals): {len(legals)}')
    # TODO: need to protect for an IndexError
    article_name = article_names[int(b_id)]
    legal = legals[int(b_id)]
    print(article_name)
#    print(legal)
    # article_name = list(article.keys())[1]
    # return article[article_name]
    # return render_template()
    # art_legal is a list of dictionaries representing the section text.
    return lt_render_template('article.html', article_name=article_name, art_legal=legal, 
                            articles=get_article_names_enumerated(db), doc_id=doc_id)


if __name__ == '__main__':
    app.run(debug=True)