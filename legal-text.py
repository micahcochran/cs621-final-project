#!/usr/bin/env python3

# external libraries
from pymongo import MongoClient
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)

# docker
# HOST = '172.17.0.2'
HOST = 'localhost'

# this works fairly well
client = MongoClient(HOST, 27017)
# connect to the database -- FIXME database will need to be abstracted at some point.
db = client.al_constitution

def get_article_names_enumerated(db):
    articles = db.legal_text.find()
    article_names = map(lambda a: a['title'], articles)
    return enumerate(article_names)

@app.route('/test1')
def index():
    articles = db.legal_text.find()
#    article_names = map(lambda a: list(a.keys())[1], articles)
    article_names = map(lambda a: a['title'], articles)

    return render_template("top.html", articles=enumerate(article_names))

# for browsing an article
@app.route('/browse/<b_id>')
def browse(b_id):
    articles = db.legal_text.find()
#    article_names = list(map(lambda a: list(a.keys())[1], articles))
    article_names = tuple(map(lambda a: a['title'], articles))
    articles = db.legal_text.find()
    legals = tuple(map(lambda a: a['legal'], articles))
    print(f'len(article_names): {len(article_names)}')
    print(f'len(legals): {len(legals)}')
    # TODO: need to protect for an IndexError
    article_name = article_names[int(b_id)]
    legal = legals[int(b_id)]
    print(article_name)
    print(legal)
    # article_name = list(article.keys())[1]
    # return article[article_name]
    # return render_template()
    # art_legal is a list of dictionaries representing the section text.
    return render_template('article.html', article_name=article_name, art_legal=legal, articles=get_article_names_enumerated(db))


if __name__ == '__main__':
    app.run(debug=True)