from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

from flask import Flask, jsonify, g, render_template, request, redirect, url_for, session
from flask_github import GitHub
from urlparse import urlparse, urljoin
from requests_oauthlib import OAuth2Session
from flask.json import jsonify
import os
import json

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key='9432818cf3f23b850773',
    consumer_secret='8814480dcbb1018338d5f46a026261e9be06199c',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)


@app.route('/')
def index():
    if 'github_token' in session:
    	target = urlparse(request.url).query
    	if target.startswith("search_term="):
    		target = target[12:]
    	lan = 'https://api.github.com/search/repositories?q='+target + '+language:assembly&sort=stars&order=desc'
    	me = github.get(lan)
    	return jsonify(me.data)

@app.route('/navigator/<name>')
def success(name):
   target = name
   return 'w %s' % target
@app.route('/navigator')
def login():
	target = urlparse(request.url).query
	if target.startswith("search_term="):
		target = target[12:]
	lan = 'https://api.github.com/search/repositories?q='+target + '+language:assembly&sort=stars&order=desc'
	return github.authorize(callback=url_for('authorized', lan=lan, _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@app.route('/navigator/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['github_token'] = (resp['access_token'], '')
    target = urlparse(request.url).query
    if target.startswith("search_term="):
    	target = target[12:]
    lan = 'https://api.github.com/search/repositories?q='+target + '+language:assembly&sort=stars&order=desc'
    me = github.get(lan)
    return redirect(url_for('index'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


if __name__ == '__main__':
    app.run()
