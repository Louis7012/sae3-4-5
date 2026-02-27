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
    # affichage des produits
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
    type_prise = """SELECT type_prise.id_type_prise, type_prise.nom_type_prise as nom
                    FROM type_prise
                    """
    mycursor.execute(type_prise)
    type_prise = mycursor.fetchall()

    sql = '''
        SELECT ligne_panier.utilisateur_id,
               ligne_panier.cable_id        AS id_cable,
               ligne_panier.quantite_panier AS quantite,
               ligne_panier.date_ajout,
               cable.prix_cable             AS prix,
               cable.nom_cable              AS nom
        FROM ligne_panier
        JOIN cable
            ON ligne_panier.cable_id = cable.id_cable
        WHERE ligne_panier.utilisateur_id = %s;
    '''

    mycursor.execute(sql, (id_client,))
    cables_panier = mycursor.fetchall()
#prix total du panier
    if len(cables_panier) >= 1:
        sql = '''
            SELECT SUM(ligne_panier.quantite_panier * cable.prix_cable) AS prix_total
            FROM ligne_panier
            JOIN cable
                ON ligne_panier.cable_id = cable.id_cable
            WHERE ligne_panier.utilisateur_id = %s;
        '''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()['prix_total']
    else:
        prix_total = 0

    return render_template('client/boutique/panier_cable.html',
                           cable=cable,
                           cable_panier=cables_panier,  # <== ici
                           prix_total=prix_total,
                           items_filtre=type_prise
                           )
