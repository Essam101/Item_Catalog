#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, All_cat, All_item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps
app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'
        ]['client_id']
APPLICATION_NAME = 'catelog'
engine = create_engine('sqlite:///catelog.db?check_same_thread=False')

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgry state token

@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Validate state Token

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

        # obtain authorization

    code = request.data

    try:

        # upgreade the authoriztion code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json',
                scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = \
            make_response(json.dumps('Filed to upgrade the authorization code'
                          ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # if there was an error in the access oken info , abort

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the ntened user

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = \
            make_response(json.dumps("Token user ID dosent't match given user id ."
                          ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

        # verify that the access token is valid for this app

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps("Token user ID dosent't match given user id ."
                          ), 401)
        print 'Token is client id dosent match app is .'
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected'
                          ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in the session for later use

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Redirct the user info

    output = ''
    output += '<h1>Welcome,'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += \
        '"style ="width: 300px;height: 300px;border-radius:150px;-webkit-border-radius:150px;-moz-border-radius:150px;">'
    flash('you are now logged in as %s' % login_session['username'])
    print 'Done!'
    return output


@app.route('/notconnect')
def notconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'access Token is Emty'
        response = make_response(json.dumps('Current user notconnect'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'in disconnect access token is %s' % access_token
    print 'username'
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('succsessfle dis conn'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Logout successfully')
        return redirect(url_for('categoryView'))
    else:
        response = make_response(json.dumps('Filed to dis connected'),
                                 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Only display the contents of an item from the category table

@app.route('/category/<int:category_id>/json')
def categoryItemJSON(category_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(All_cat).filter_by(id=category_id).one()
    items = \
        session.query(All_item).filter_by(category_id=category_id).all()
    return jsonify(categoryItems=[i.serialize for i in items])


# View content of one item

@app.route('/category/item/<int:item_id>/json/')
def ItemJSON(item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(All_item).filter_by(id=item_id).one()
    return jsonify(Item=items.serialize)


# View the content of a category table

@app.route('/category/json/')
def categoryJson():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(All_cat).all()
    return jsonify(category=[r.serialize for r in category])


# categorys view

@app.route('/')
@app.route('/category/')
def categoryView():
    category = session.query(All_cat).all()
    loggedIn = 'username' in login_session
    return render_template('category.html', category=category,
                           loggedIn=loggedIn)


# items view

@app.route('/category/<int:category_id>/')
def itemView(category_id):
    category = session.query(All_cat).filter_by(id=category_id).one()
    items = session.query(All_item).filter_by(category_id=category_id)
    loggedIn = 'username' in login_session
    return render_template('item.html', category=category, items=items,
                           loggedIn=loggedIn)


# creat new item

@app.route('/category/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem(category_id):
    category = session.query(All_cat).all()
    if request.method == 'POST':
        newItem = All_item(name=request.form['name'],
                           description=request.form['description'],
                           category_id=category_id)
        session.add(newItem)
        session.commit()
        flash('Done Create New Item !')
        return redirect(url_for('itemView', category_id=category_id))
    else:
        if 'username' not in login_session:
            return redirect('/login/')

        return render_template('newCate.html', category_id=category_id)


# Edit item

@app.route('/category/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def edit_Item(category_id, item_id):
    editItem = session.query(All_item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
            session.add(editItem)
            session.commit()

        if request.form['description']:
            editItem.description = request.form['description']
            session.add(editItem)
            session.commit()
            flash('Done Edit item !')
        return redirect(url_for('categoryView',
                        category_id=category_id))
    else:
        if 'username' not in login_session:
            return redirect('/login/')
        return render_template('editItem.html',
                               category_id=category_id,
                               item_id=item_id, i=editItem)


# Delete item

@app.route('/category/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    itemDelete = session.query(All_item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemDelete)
        session.commit()
        flash('Done Delet item')
        return redirect(url_for('itemView', category_id=category_id))
    else:
        if 'username' not in login_session:
            return redirect('/login/')
        return render_template('deleteCate.html', i=itemDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
