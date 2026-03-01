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

########################
# P4 - Guilian LEVEQUE #
########################

@app.route('/admin/cable/show')
def show_admin_cable():
    mycursor = get_db().cursor()
    sql = "SELECT id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, marque, photo, stock, type_prise_id, longueur_id FROM cable;"
    mycursor.execute(sql)
    liste_cables = mycursor.fetchall()
    return render_template('admin/cable/show_cable.html', cables=liste_cables)

@app.route('/admin/cable/edit')
def edit_admin_cable():
    mycursor = get_db().cursor()
    id_cable = request.args.get('id_cable')
    sql = "SELECT id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, marque, photo, stock, type_prise_id, longueur_id FROM cable WHERE id_cable = %s;"
    mycursor.execute(sql, id_cable)
    cable = mycursor.fetchone()
    sql = "SELECT * FROM type_prise;"
    mycursor.execute(sql)
    type_prise = mycursor.fetchall()
    return render_template('admin/cable/edit_cable.html', cable=cable, type_prise=type_prise)

@app.route('/admin/cable/valid_edit', methods=['POST'])
def valid_edit_admin_cable():
    mycursor = get_db().cursor()
    id_cable = request.form.get('id_cable')
    nom = request.form.get('nom')
    prix = request.form.get('prix')
    photo = request.form.get('image')
    type_prise = request.form.get('type_prise_id')
    marque = request.form.get('marque')
    stock = request.form.get('stock')
    sql = "UPDATE cable SET nom_cable=%s, prix_cable=%s, photo=%s, type_prise_id=%s, marque=%s, stock=%s WHERE id_cable = %s;"
    mycursor.execute(sql, (nom, prix, photo, type_prise, marque, stock, id_cable))
    get_db().commit()
    return redirect('/admin/cable/show')


@app.route('/admin/commandes/show')
def show_admin_commande():
    mycursor = get_db().cursor()
    id_commande = request.args.get('id_commande')
    cables_commande = None
    if id_commande:
        sql_details = """
                      SELECT lc.commande_id AS id,
                             c.nom_cable AS nom,
                             lc.quantite_commande AS quantite,
                             lc.prix,
                             (lc.quantite_commande * lc.prix) AS prix_ligne
                      FROM ligne_commande lc
                      JOIN cable c ON lc.cable_id = c.id_cable
                      WHERE lc.commande_id = %s;
                      """
        mycursor.execute(sql_details, (id_commande,))
        cables_commande = mycursor.fetchall()
    sql_commandes = """
                    SELECT c.id_commande,
                           u.login,
                           c.date_achat,
                           SUM(lc.quantite_commande)           AS nbr_cables,
                           SUM(lc.quantite_commande * lc.prix) AS prix_total,
                           e.libelle,
                           c.etat_id
                    FROM commande c
                    JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
                    JOIN etat e ON c.etat_id = e.id_etat
                    LEFT JOIN ligne_commande lc ON c.id_commande = lc.commande_id
                    GROUP BY c.id_commande
                    ORDER BY c.date_achat DESC;
                    """
    mycursor.execute(sql_commandes)
    commandes_liste = mycursor.fetchall()
    return render_template('admin/commandes/show.html', commandes=commandes_liste, cables_commande=cables_commande, commande_adresses=[])

@app.route('/admin/commandes/valider', methods=['POST'])
def valid_admin_commande():
    mycursor = get_db().cursor()
    id_commande = request.form.get('id_commande')
    sql = "UPDATE commande SET etat_id = 3 WHERE id_commande = %s;"
    mycursor.execute(sql, id_commande)
    get_db().commit()
    return redirect('/admin/commandes/show')

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

