#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_cable = Blueprint('client_cable', __name__,
                        template_folder='templates')

@client_cable.route('/client/index')
@client_cable.route('/client/cable/show')              # remplace /client
def client_cable_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''   selection des cables   '''
    list_param = []
    condition_and = ""
    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''
    sql = '''
          SELECT id_cable   AS id_cable
               , nom_cable  AS nom
               , prix_cable AS prix
               , stock      AS stock
               , photo      AS image
          FROM cable
          ORDER BY nom_cable;
          '''
    mycursor.execute(sql)
    cable = mycursor.fetchall()
    cable = cable


    # pour le filtre
    type_prise = '''SELECT DISTINCT nom_type_prise as nom
    FROM type_prise;'''
    mycursor.execute(type_prise)
    type_prise = mycursor.fetchall()


    cables_panier = []

    if len(cables_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = None
    else:
        prix_total = None
    return render_template('client/boutique/panier_cable.html'
                           , cable=cable
                           , cables_panier=cables_panier
                           #, prix_total=prix_total
                           , items_filtre=type_prise
                           )