#!/usr/bin/env python3

# internal libraries
from typing import Optional

# external libraries
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired # , Email

# app library imports
from database import (db, add_book, has_book, get_books, get_book, set_book_editable,
                      delete_book, is_book_editable)


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
def search_snippet(rec, query: str, snippet_length:int=400) -> Optional[str]:
    """create a string snippet from a search record"""
    # do some preprocessing on results to create snippets of text search results
    # prioritize titles
    if query.lower() in rec['title'].lower():
        return rec['title']
    
    # print(f'rec.keys(): {rec.keys()}')
    # print(f'rec' {rec})

    # look at the articles/amendments for their subtitles
    for art in rec['legal']:
        # print(f"type(section) {type(section)}")
        # print(f"art {art}")
        # print(f'rec.keys(): {rec.keys()}')
        # print(f'isinstance(art, dict): {isinstance(art, dict)}')
        if isinstance(art, dict) and query.lower() in art['subtitle'].lower():
            return f"{art['subtype']} {art['number']} - {art['subtitle']}"

    # look for a match in the contents
    for art in rec['legal']:
        # section is a list of strings
        for section in art['content']:
            # for para in section:
            # print(type(section))
                # if 'declaration' in para.lower():
                #    print('MATCH')
            if query.lower() in section.lower():
                # return f"{art['subtype']} {art['number']} - {art['subtitle']}<br>" + section
                half_snip = (snippet_length - len(query)) // 2
                idx = section.find(query)
                if idx - half_snip < 0:
                    b_idx = 0
                else:
                    b_idx = idx - half_snip
                t_idx = idx + len(query) + half_snip
                
                return  f"{art['subtype']} {art['number']} - {art['subtitle']}<br>" + \
                        f"…{section[b_idx:t_idx]}…"

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
    # num_results = len(results)

    # create snippets from search results, removing results that are None values
    snip_results = list(filter(lambda x: x is not None, 
                            map(lambda r: search_snippet(r,query), results)))
#    snip_results = list(map(lambda r: search_snippet(r,query), results))
    num_results = len(snip_results)
    return lt_render_template('search_results.html', query=query, 
                                snip_results=snip_results, num_results=num_results)
    # return f"This is plumbing for search.  What you searched for was this '{query}' from the document '{doc_id}'."


@app.route('/settings')
def settings():
    return render_template('settings.html', books=get_books(), \
            is_book_editable=is_book_editable)


@app.route('/set_tgl_bk_editable/<collection>')
def set_tgl_bk_editable(collection):
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
    import os
#    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
