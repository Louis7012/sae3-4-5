#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__, template_folder='templates')


def maj_stock_cable(mycursor, id_cable):
    """Calcule le stock total des déclinaisons et met à jour la table cable."""
    mycursor.execute("SELECT SUM(stock) AS total FROM declinaison_cable WHERE cable_id=%s", id_cable)
    row = mycursor.fetchone()
    nouveau_stock = row['total'] if row['total'] else 0
    mycursor.execute("UPDATE cable SET stock=%s WHERE id_cable=%s", (nouveau_stock, id_cable))


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.form.get('id_cable')
    quantite = int(request.form.get('quantite', 1))
    id_declinaison = request.form.get('id_declinaison_cable', None)

    # Récupérer toutes les déclinaisons disponibles pour ce câble
    mycursor.execute(
        "SELECT id_declinaison_cable, stock, prix FROM declinaison_cable WHERE cable_id=%s AND stock>0",
        id_cable
    )
    declinaisons = mycursor.fetchall()
    nb_decl = len(declinaisons)

    # Si une déclinaison spécifique a été fournie (depuis la page de choix)
    if id_declinaison:
        _ajouter_avec_declinaison(mycursor, id_client, id_cable, id_declinaison, quantite)
        get_db().commit()
        return redirect('/client/cable/show')

    if nb_decl == 0:
        # Câble sans déclinaison : traitement direct sur la table cable
        mycursor.execute("SELECT stock, prix_cable FROM cable WHERE id_cable=%s", id_cable)
        cab = mycursor.fetchone()
        if not cab or cab['stock'] < quantite:
            flash("Stock insuffisant.", 'alert-warning')
            return redirect('/client/cable/show')
        mycursor.execute(
            "SELECT id_panier FROM ligne_panier WHERE utilisateur_id=%s AND cable_id=%s AND declinaison_cable_id IS NULL",
            (id_client, id_cable)
        )
        existing = mycursor.fetchone()
        if existing:
            mycursor.execute(
                "UPDATE ligne_panier SET quantite_panier=quantite_panier+%s WHERE id_panier=%s",
                (quantite, existing['id_panier'])
            )
        else:
            mycursor.execute(
                "INSERT INTO ligne_panier(cable_id, utilisateur_id, declinaison_cable_id, quantite_panier, date_ajout) VALUES(%s,%s,NULL,%s,NOW())",
                (id_cable, id_client, quantite)
            )
        mycursor.execute("UPDATE cable SET stock=stock-%s WHERE id_cable=%s", (quantite, id_cable))
        get_db().commit()
        return redirect('/client/cable/show')

    elif nb_decl == 1:
        # Une seule déclinaison : ajout automatique
        id_declinaison = declinaisons[0]['id_declinaison_cable']
        _ajouter_avec_declinaison(mycursor, id_client, id_cable, id_declinaison, quantite)
        get_db().commit()
        return redirect('/client/cable/show')

    else:
        # Plusieurs déclinaisons : afficher la page de choix
        mycursor.execute(
            "SELECT id_cable, nom_cable AS nom, photo AS image, prix_cable AS prix FROM cable WHERE id_cable=%s",
            id_cable
        )
        cable = mycursor.fetchone()
        mycursor.execute("""
            SELECT dc.id_declinaison_cable, dc.stock, dc.prix,
                   l.nom_longueur, co.nom_couleur, co.code_hex, co.id_couleur, l.id_longueur
            FROM declinaison_cable dc
            JOIN longueur l ON dc.longueur_id = l.id_longueur
            JOIN couleur co ON dc.couleur_id = co.id_couleur
            WHERE dc.cable_id=%s AND dc.stock>0
        """, id_cable)
        declinaisons_detail = mycursor.fetchall()
        return render_template(
            'client/boutique/declinaison_cable.html',
            declinaisons=declinaisons_detail, cable=cable, quantite=quantite
        )


def _ajouter_avec_declinaison(mycursor, id_client, id_cable, id_declinaison, quantite):
    """Ajoute une déclinaison dans le panier et décrémente le stock."""
    mycursor.execute(
        "SELECT stock, prix FROM declinaison_cable WHERE id_declinaison_cable=%s", id_declinaison
    )
    decl = mycursor.fetchone()
    if not decl or decl['stock'] < quantite:
        flash("Stock insuffisant pour cette déclinaison.", 'alert-warning')
        return
    mycursor.execute(
        "SELECT id_panier FROM ligne_panier WHERE utilisateur_id=%s AND declinaison_cable_id=%s",
        (id_client, id_declinaison)
    )
    existing = mycursor.fetchone()
    if existing:
        mycursor.execute(
            "UPDATE ligne_panier SET quantite_panier=quantite_panier+%s WHERE id_panier=%s",
            (quantite, existing['id_panier'])
        )
    else:
        mycursor.execute(
            "INSERT INTO ligne_panier(cable_id, utilisateur_id, declinaison_cable_id, quantite_panier, date_ajout) VALUES(%s,%s,%s,%s,NOW())",
            (id_cable, id_client, id_declinaison, quantite)
        )
    mycursor.execute(
        "UPDATE declinaison_cable SET stock=stock-%s WHERE id_declinaison_cable=%s",
        (quantite, id_declinaison)
    )
    maj_stock_cable(mycursor, id_cable)


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_panier = request.form.get('id_panier')
    mycursor.execute(
        "SELECT cable_id, declinaison_cable_id, quantite_panier FROM ligne_panier WHERE id_panier=%s AND utilisateur_id=%s",
        (id_panier, id_client)
    )
    item = mycursor.fetchone()
    if not item:
        return redirect('/client/cable/show')
    if item['quantite_panier'] > 1:
        mycursor.execute("UPDATE ligne_panier SET quantite_panier=quantite_panier-1 WHERE id_panier=%s", id_panier)
        if item['declinaison_cable_id']:
            mycursor.execute("UPDATE declinaison_cable SET stock=stock+1 WHERE id_declinaison_cable=%s",
                             item['declinaison_cable_id'])
            maj_stock_cable(mycursor, item['cable_id'])
        else:
            mycursor.execute("UPDATE cable SET stock=stock+1 WHERE id_cable=%s", item['cable_id'])
    else:
        mycursor.execute("DELETE FROM ligne_panier WHERE id_panier=%s", id_panier)
        if item['declinaison_cable_id']:
            mycursor.execute("UPDATE declinaison_cable SET stock=stock+1 WHERE id_declinaison_cable=%s",
                             item['declinaison_cable_id'])
            maj_stock_cable(mycursor, item['cable_id'])
        else:
            mycursor.execute("UPDATE cable SET stock=stock+1 WHERE id_cable=%s", item['cable_id'])
    get_db().commit()
    return redirect('/client/cable/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_panier = request.form.get('id_panier')
    mycursor.execute(
        "SELECT cable_id, declinaison_cable_id, quantite_panier FROM ligne_panier WHERE id_panier=%s AND utilisateur_id=%s",
        (id_panier, id_client)
    )
    item = mycursor.fetchone()
    if item:
        mycursor.execute("DELETE FROM ligne_panier WHERE id_panier=%s", id_panier)
        if item['declinaison_cable_id']:
            mycursor.execute("UPDATE declinaison_cable SET stock=stock+%s WHERE id_declinaison_cable=%s",
                             (item['quantite_panier'], item['declinaison_cable_id']))
            maj_stock_cable(mycursor, item['cable_id'])
        else:
            mycursor.execute("UPDATE cable SET stock=stock+%s WHERE id_cable=%s",
                             (item['quantite_panier'], item['cable_id']))
        get_db().commit()
    return redirect('/client/cable/show')


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("SELECT cable_id, declinaison_cable_id, quantite_panier FROM ligne_panier WHERE utilisateur_id=%s", id_client)
    items = mycursor.fetchall()
    for item in items:
        if item['declinaison_cable_id']:
            mycursor.execute("UPDATE declinaison_cable SET stock=stock+%s WHERE id_declinaison_cable=%s",
                             (item['quantite_panier'], item['declinaison_cable_id']))
            maj_stock_cable(mycursor, item['cable_id'])
        else:
            mycursor.execute("UPDATE cable SET stock=stock+%s WHERE id_cable=%s",
                             (item['quantite_panier'], item['cable_id']))
    mycursor.execute("DELETE FROM ligne_panier WHERE utilisateur_id=%s", id_client)
    get_db().commit()
    return redirect('/client/cable/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types', None)
    if filter_word and len(filter_word) > 0:
        session['filter_word'] = filter_word.strip()
    else:
        session.pop('filter_word', None)
    if filter_prix_min and filter_prix_min.isdigit():
        session['filter_prix_min'] = filter_prix_min
    else:
        session.pop('filter_prix_min', None)
    if filter_prix_max and filter_prix_max.isdigit():
        session['filter_prix_max'] = filter_prix_max
    else:
        session.pop('filter_prix_max', None)
    if filter_types:
        session['filter_types'] = filter_types
    else:
        session.pop('filter_types', None)
    return redirect('/client/cable/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    return redirect('/client/cable/show')
