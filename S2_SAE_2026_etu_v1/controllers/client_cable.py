#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, session
from connexion_db import get_db

client_cable = Blueprint('client_cable', __name__, template_folder='templates')


@client_cable.route('/client/index')
@client_cable.route('/client/cable/show')
def client_cable_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Filtres en session
    where_clauses = []
    params = []
    if session.get('filter_word'):
        where_clauses.append("c.nom_cable LIKE %s")
        params.append('%' + session['filter_word'] + '%')
    if session.get('filter_types'):
        placeholders = ','.join(['%s'] * len(session['filter_types']))
        where_clauses.append("c.type_prise_id IN (" + placeholders + ")")
        params.extend(session['filter_types'])
    if session.get('filter_prix_min'):
        where_clauses.append("c.prix_cable >= %s")
        params.append(session['filter_prix_min'])
    if session.get('filter_prix_max'):
        where_clauses.append("c.prix_cable <= %s")
        params.append(session['filter_prix_max'])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Sélection des câbles avec statistiques (sans COALESCE ni CASE WHEN)
    sql = """
        SELECT c.id_cable, c.nom_cable AS nom, c.photo AS image,
               c.prix_cable AS prix, c.stock,
               COUNT(DISTINCT dc.id_declinaison_cable) AS nb_declinaison,
               AVG(a.note) AS moy_notes,
               COUNT(DISTINCT a.id_avis) AS nb_notes,
               COUNT(DISTINCT com.id_commentaire) AS nb_avis
        FROM cable c
        LEFT JOIN declinaison_cable dc ON dc.cable_id = c.id_cable
        LEFT JOIN avis a ON a.cable_id = c.id_cable
        LEFT JOIN commentaire com ON com.cable_id = c.id_cable
            AND com.commentaire_parent_id IS NULL
        """ + where_sql + """
        GROUP BY c.id_cable
        ORDER BY c.nom_cable
    """
    mycursor.execute(sql, params)
    cables = mycursor.fetchall()

    # Ajouter l'indicateur wishlist pour chaque câble (True/False)
    for cable in cables:
        mycursor.execute("""
            SELECT COUNT(*) AS nb FROM liste_envies
            WHERE utilisateur_id = %s AND cable_id = %s
        """, (id_client, cable['id_cable']))
        cable['liste_envie'] = mycursor.fetchone()['nb']

    # Panier du client
    mycursor.execute("""
        SELECT lp.id_panier, lp.cable_id AS id_cable, lp.declinaison_cable_id,
               lp.quantite_panier AS quantite, lp.date_ajout,
               c.prix_cable AS prix, c.nom_cable AS nom,
               l.nom_longueur, co.nom_couleur
        FROM ligne_panier lp
        JOIN cable c ON lp.cable_id = c.id_cable
        LEFT JOIN declinaison_cable dc ON lp.declinaison_cable_id = dc.id_declinaison_cable
        LEFT JOIN longueur l ON dc.longueur_id = l.id_longueur
        LEFT JOIN couleur co ON dc.couleur_id = co.id_couleur
        WHERE lp.utilisateur_id = %s
    """, (id_client,))
    cables_panier = mycursor.fetchall()

    # Utiliser le prix de la déclinaison si elle existe
    for item in cables_panier:
        if item['declinaison_cable_id']:
            mycursor.execute("SELECT prix FROM declinaison_cable WHERE id_declinaison_cable = %s",
                             item['declinaison_cable_id'])
            decl = mycursor.fetchone()
            if decl and decl['prix']:
                item['prix'] = decl['prix']

    prix_total = 0
    for item in cables_panier:
        prix_total = prix_total + item['prix'] * item['quantite']

    mycursor.execute("SELECT id_type_prise, nom_type_prise AS nom FROM type_prise")
    type_prise = mycursor.fetchall()

    return render_template('client/boutique/panier_cable.html',
                           cable=cables, cable_panier=cables_panier,
                           prix_total=prix_total, items_filtre=type_prise)
