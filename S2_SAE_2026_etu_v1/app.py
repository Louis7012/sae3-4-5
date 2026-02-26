#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from flask import Blueprint


from controllers.auth_security import *
from controllers.fixtures_load import *

from controllers.client_cable import *
from controllers.client_panier import *
from controllers.client_commande import *
from controllers.client_commentaire import *
from controllers.client_coordonnee import *

from controllers.admin_cable import *
from controllers.admin_declinaison_cable import *
from controllers.admin_commande import *
from controllers.admin_type_prise import *
from controllers.admin_dataviz import *
from controllers.admin_commentaire import *
from controllers.client_liste_envies import *

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

from flask import session, g
import pymysql.cursors

import os                                 # à ajouter
from dotenv import load_dotenv            # à ajouter
load_dotenv()                             # à ajouter

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        #
        db = g._database = pymysql.connect(
            host="localhost",
            user="rpeig",
            password="secret",
            database="s2_BDD",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # à activer sur les machines personnelles :
        activate_db_options(db)
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_accueil():
    if 'role' in session:
        if session['role'] == 'ROLE_admin':
            return redirect('/admin/commande/index')
        else:
            return redirect('/client/cable/show')
    return render_template('auth/layout.html')

##################
# Authentification
##################

# Middleware de sécurité

@app.before_request
def before_request():
     if request.path.startswith('/admin') or request.path.startswith('/client'):
        print('session start with /admin or /client')
        if 'role' not in session:
            return redirect('/login')
        else:
            print('role',session['role'])
            if (request.path.startswith('/client') and session['role'] != 'ROLE_client') or (request.path.startswith('/admin') and session['role'] != 'ROLE_admin'):
                print('pb de route : ', session['role'], request.path.title(), ' => deconnexion')
                session.pop('login', None)
                session.pop('role', None)
                flash("PB route / rôle / autorisation", "alert-warning")
                return redirect('/logout')



app.register_blueprint(auth_security)
app.register_blueprint(fixtures_load)

app.register_blueprint(client_cable)
app.register_blueprint(client_commande)
app.register_blueprint(client_commentaire)
app.register_blueprint(client_panier)
app.register_blueprint(client_coordonnee)
app.register_blueprint(client_liste_envies)

app.register_blueprint(admin_cable)
app.register_blueprint(admin_declinaison_cable)
app.register_blueprint(admin_commande)
app.register_blueprint(admin_type_prise)
app.register_blueprint(admin_dataviz)
app.register_blueprint(admin_commentaire)


if __name__ == '__main__':
    app.run()

