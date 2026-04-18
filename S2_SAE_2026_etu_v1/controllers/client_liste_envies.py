#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__, template_folder='templates')


@client_liste_envies.route('/client/envie/add', methods=['GET'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.args.get('id_cable')
    # Vérifier si déjà dans la wishlist
    mycursor.execute("SELECT cable_id FROM liste_envies WHERE utilisateur_id=%s AND cable_id=%s",
                     (id_client, id_cable))
    existing = mycursor.fetchone()
    if existing:
        # Supprimer (toggle)
        mycursor.execute("DELETE FROM liste_envies WHERE utilisateur_id=%s AND cable_id=%s",
                         (id_client, id_cable))
    else:
        # Ajouter avec rang maximum+1
        mycursor.execute("SELECT MAX(rang) AS max_rang FROM liste_envies WHERE utilisateur_id=%s", id_client)
        row = mycursor.fetchone()
        if row['max_rang'] is None:
            next_rang = 1
        else:
            next_rang = row['max_rang'] + 1
        mycursor.execute("INSERT INTO liste_envies(utilisateur_id, cable_id, date_ajout, rang) VALUES(%s,%s,NOW(),%s)",
                         (id_client, id_cable, next_rang))
    get_db().commit()
    return redirect('/client/cable/show')


@client_liste_envies.route('/client/envie/delete', methods=['GET'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.args.get('id_cable')
    mycursor.execute("SELECT rang FROM liste_envies WHERE utilisateur_id=%s AND cable_id=%s", (id_client, id_cable))
    row = mycursor.fetchone()
    if row:
        rang = row['rang']
        mycursor.execute("DELETE FROM liste_envies WHERE utilisateur_id=%s AND cable_id=%s", (id_client, id_cable))
        # Réajuster les rangs
        mycursor.execute("UPDATE liste_envies SET rang=rang-1 WHERE utilisateur_id=%s AND rang>%s",
                         (id_client, rang))
    get_db().commit()
    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/show', methods=['GET'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    mycursor.execute("""
        SELECT le.*, c.nom_cable AS nom, c.photo AS image, c.prix_cable AS prix, c.id_cable
        FROM liste_envies le
        JOIN cable c ON le.cable_id=c.id_cable
        WHERE le.utilisateur_id=%s
        ORDER BY le.rang ASC
    """, id_client)
    cables_liste_envies = mycursor.fetchall()

    mycursor.execute("""
        SELECT h.*, c.nom_cable AS nom, c.photo AS image, c.prix_cable AS prix
        FROM historique h
        JOIN cable c ON h.cable_id=c.id_cable
        WHERE h.utilisateur_id=%s
        ORDER BY h.date_consultation DESC
        LIMIT 6
    """, id_client)
    cables_historique = mycursor.fetchall()

    mycursor.execute("SELECT COUNT(*) AS nb FROM liste_envies WHERE utilisateur_id=%s", id_client)
    nb_liste_envies = mycursor.fetchone()['nb']

    mycursor.execute("SELECT COUNT(*) AS nb FROM historique WHERE utilisateur_id=%s", id_client)
    nb_historique = mycursor.fetchone()['nb']

    return render_template('client/liste_envies/liste_envies_show.html',
                           cables_liste_envies=cables_liste_envies,
                           cables_historique=cables_historique,
                           nb_liste_envies=nb_liste_envies,
                           nb_historique=nb_historique)


@client_liste_envies.route('/client/envies/up', methods=['GET'])
@client_liste_envies.route('/client/envies/down', methods=['GET'])
@client_liste_envies.route('/client/envies/last', methods=['GET'])
@client_liste_envies.route('/client/envies/first', methods=['GET'])
def client_liste_envies_cable_move():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.args.get('id_cable')
    direction = request.path.split('/')[-1]  # up, down, first, last

    mycursor.execute("SELECT rang FROM liste_envies WHERE utilisateur_id=%s AND cable_id=%s", (id_client, id_cable))
    row = mycursor.fetchone()
    if not row:
        return redirect('/client/envies/show')

    rang_actuel = row['rang']
    mycursor.execute("SELECT COUNT(*) AS nb FROM liste_envies WHERE utilisateur_id=%s", id_client)
    total = mycursor.fetchone()['nb']

    if direction == 'up' and rang_actuel > 1:
        # Échanger avec rang-1
        mycursor.execute("UPDATE liste_envies SET rang=%s WHERE utilisateur_id=%s AND rang=%s",
                         (rang_actuel, id_client, rang_actuel - 1))
        mycursor.execute("UPDATE liste_envies SET rang=%s WHERE utilisateur_id=%s AND cable_id=%s",
                         (rang_actuel - 1, id_client, id_cable))
    elif direction == 'down' and rang_actuel < total:
        mycursor.execute("UPDATE liste_envies SET rang=%s WHERE utilisateur_id=%s AND rang=%s",
                         (rang_actuel, id_client, rang_actuel + 1))
        mycursor.execute("UPDATE liste_envies SET rang=%s WHERE utilisateur_id=%s AND cable_id=%s",
                         (rang_actuel + 1, id_client, id_cable))
    elif direction == 'first':
        mycursor.execute("UPDATE liste_envies SET rang=rang+1 WHERE utilisateur_id=%s AND rang < %s",
                         (id_client, rang_actuel))
        mycursor.execute("UPDATE liste_envies SET rang=1 WHERE utilisateur_id=%s AND cable_id=%s",
                         (id_client, id_cable))
    elif direction == 'last':
        mycursor.execute("UPDATE liste_envies SET rang=rang-1 WHERE utilisateur_id=%s AND rang > %s",
                         (id_client, rang_actuel))
        mycursor.execute("UPDATE liste_envies SET rang=%s WHERE utilisateur_id=%s AND cable_id=%s",
                         (total, id_client, id_cable))

    get_db().commit()
    return redirect('/client/envies/show')


def client_historique_add(cable_id, client_id):
    """Ajoute ou met à jour l'historique de consultation, max 6 articles."""
    mycursor = get_db().cursor()
    # Vérifier si déjà dans l'historique
    mycursor.execute("SELECT id_historique FROM historique WHERE utilisateur_id=%s AND cable_id=%s",
                     (client_id, cable_id))
    existing = mycursor.fetchone()
    if existing:
        mycursor.execute("UPDATE historique SET date_consultation=NOW(), nb_consultations=nb_consultations+1 WHERE id_historique=%s",
                         existing['id_historique'])
    else:
        # Compter le nombre d'articles dans l'historique
        mycursor.execute("SELECT COUNT(*) AS nb FROM historique WHERE utilisateur_id=%s", client_id)
        nb = mycursor.fetchone()['nb']
        if nb >= 6:
            # Supprimer le plus ancien
            mycursor.execute("DELETE FROM historique WHERE utilisateur_id=%s ORDER BY date_consultation ASC LIMIT 1",
                             client_id)
        mycursor.execute("INSERT INTO historique(utilisateur_id, cable_id, date_consultation, nb_consultations) VALUES(%s,%s,NOW(),1)",
                         (client_id, cable_id))
    # Supprimer entrées > 1 mois
    mycursor.execute("DELETE FROM historique WHERE utilisateur_id=%s AND date_consultation < DATE_SUB(NOW(), INTERVAL 1 MONTH)",
                     client_id)
    get_db().commit()
