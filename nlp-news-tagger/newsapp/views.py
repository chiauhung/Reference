from newsapp import app
from flask import request, render_template,url_for, redirect, session
from ast import literal_eval
import pandas as pd
import json
import sys
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'resources')
df = pd.read_csv(os.path.join(APP_STATIC, 'thestar2_travel_tag.csv'))
df['article_tag'] = df['article_tag'].fillna('')

@app.route('/')
def index():
	return "Hello from The Star - Lee Chiau Hung"

@app.route('/news', methods=['GET'])
def news_list():
	news = df[['index','Title','Author','Publish Date','article_tag']].to_dict(orient='records')
	return render_template('newslist.html', header = "All News", news_list = news)

@app.route('/tag', methods=['GET','POST'])
def tag_list():
	if request.method == 'POST':
		tag_name = request.form['submit_button']
		return redirect(url_for('tag_list', tag_name=tag_name))

	tag = request.args.get("tag_name")
	news = df[df['article_tag'].map(lambda x: tag in x)].to_dict(orient='records')
	return render_template('newslist.html', header = 'News with Tag {} <a href = "/news">Back</a>'.format(tag), news_list = news)
@app.route('/<nid>', methods=['GET','POST'])
def news_content(nid):
	if request.method == 'POST':
		tag_name = request.form['submit_button']
		return redirect(url_for('tag_list', tag_name=tag_name))
	news_id = int(nid)
	article = df[df['index']==news_id]
	text = article['Content'].iloc[0]
	title = article['Title'].iloc[0]
	tags = article['article_tag'].iloc[0].split("|")
	return render_template('article.html', news_id = news_id, title=title, tags=tags, article_html=text)

