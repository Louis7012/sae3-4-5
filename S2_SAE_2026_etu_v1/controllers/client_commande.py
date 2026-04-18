#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__, template_folder='templates')


@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    mycursor.execute("""
        SELECT lp.id_panier, lp.cable_id, lp.declinaison_cable_id, lp.quantite_panier,
               c.nom_cable, c.prix_cable, dc.prix AS prix_declinaison,
               l.nom_longueur, co.nom_couleur
        FROM ligne_panier lp
        JOIN cable c ON lp.cable_id=c.id_cable
        LEFT JOIN declinaison_cable dc ON lp.declinaison_cable_id=dc.id_declinaison_cable
        LEFT JOIN longueur l ON dc.longueur_id=l.id_longueur
        LEFT JOIN couleur co ON dc.couleur_id=co.id_couleur
        WHERE lp.utilisateur_id=%s
    """, id_client)
    cables_panier = mycursor.fetchall()

    if not cables_panier:
        flash("Panier vide", "alert-warning")
        return redirect('/client/cable/show')

    # Calculer le prix effectif : déclinaison si dispo, sinon prix câble
    for item in cables_panier:
        if item['prix_declinaison']:
            item['prix_cable'] = item['prix_declinaison']

    prix_total = 0
    for item in cables_panier:
        prix_total = prix_total + item['prix_cable'] * item['quantite_panier']

    # Adresses disponibles
    mycursor.execute("""SELECT * FROM adresse WHERE utilisateur_id=%s AND est_valide=1
                        ORDER BY est_favorite DESC""", id_client)
    adresses = mycursor.fetchall()
    id_adresse_fav = next((a['id_adresse'] for a in adresses if a['est_favorite']), None)

    return render_template('client/boutique/panier_validation_adresses.html',
                           cables_panier=cables_panier, prix_total=prix_total,
                           adresses=adresses, id_adresse_fav=id_adresse_fav, validation=1)


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    adresse_livraison_id = request.form.get('adresse_livraison_id')
    adresse_facturation_id = request.form.get('adresse_facturation_id')

    mycursor.execute("""
        SELECT lp.id_panier, lp.cable_id, lp.declinaison_cable_id, lp.quantite_panier,
               c.prix_cable, dc.prix AS prix_declinaison
        FROM ligne_panier lp
        JOIN cable c ON lp.cable_id=c.id_cable
        LEFT JOIN declinaison_cable dc ON lp.declinaison_cable_id=dc.id_declinaison_cable
        WHERE lp.utilisateur_id=%s
    """, id_client)
    items = mycursor.fetchall()
    # Utiliser le prix de la déclinaison si disponible
    for item in items:
        if item['prix_declinaison']:
            item['prix_cable'] = item['prix_declinaison']

    if not items:
        flash("Panier vide", "alert-warning")
        return redirect('/client/cable/show')

    mycursor.execute("""INSERT INTO commande(date_achat, etat_id, utilisateur_id, adresse_livraison_id, adresse_facturation_id)
                        VALUES(CURDATE(), 1, %s, %s, %s)""",
                     (id_client, adresse_livraison_id or None, adresse_facturation_id or None))
    mycursor.execute("SELECT LAST_INSERT_ID() AS id")
    id_commande = mycursor.fetchone()['id']

    for item in items:
        mycursor.execute("""INSERT INTO ligne_commande(cable_id, commande_id, declinaison_cable_id, quantite_commande, prix)
                            VALUES(%s,%s,%s,%s,%s)""",
                         (item['cable_id'], id_commande, item['declinaison_cable_id'],
                          item['quantite_panier'], item['prix_cable']))

    # Retirer les articles de la wishlist s'ils ont été commandés
    for item in items:
        mycursor.execute("DELETE FROM liste_envies WHERE utilisateur_id=%s AND cable_id=%s",
                         (id_client, item['cable_id']))

    # Mettre à jour adresse favorite (dernière utilisée)
    if adresse_livraison_id:
        mycursor.execute("UPDATE adresse SET est_favorite=0 WHERE utilisateur_id=%s", id_client)
        mycursor.execute("UPDATE adresse SET est_favorite=1 WHERE id_adresse=%s AND utilisateur_id=%s",
                         (adresse_livraison_id, id_client))

    mycursor.execute("DELETE FROM ligne_panier WHERE utilisateur_id=%s", id_client)
    get_db().commit()

    flash("Commande validée avec succès !", "alert-success")
    return redirect('/client/commande/show')


@client_commande.route('/client/commande/show', methods=['GET', 'POST'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("""
        SELECT c.id_commande, c.date_achat, c.etat_id, e.libelle,
               SUM(lc.quantite_commande) AS nbr_cables,
               SUM(lc.prix * lc.quantite_commande) AS prix_total
        FROM commande c
        LEFT JOIN ligne_commande lc ON lc.commande_id=c.id_commande
        JOIN etat e ON c.etat_id=e.id_etat
        WHERE c.utilisateur_id=%s
        GROUP BY c.id_commande, c.date_achat, c.etat_id, e.libelle
        ORDER BY c.etat_id ASC, c.date_achat DESC
    """, id_client)
    commandes = mycursor.fetchall()

    cables_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande:
        mycursor.execute("""
            SELECT ca.nom_cable, lc.quantite_commande, lc.prix,
                   lc.prix * lc.quantite_commande AS prix_total,
                   l.nom_longueur, co.nom_couleur
            FROM ligne_commande lc
            JOIN cable ca ON lc.cable_id=ca.id_cable
            LEFT JOIN declinaison_cable dc ON lc.declinaison_cable_id=dc.id_declinaison_cable
            LEFT JOIN longueur l ON dc.longueur_id=l.id_longueur
            LEFT JOIN couleur co ON dc.couleur_id=co.id_couleur
            WHERE lc.commande_id=%s
        """, id_commande)
        cables_commande = mycursor.fetchall()

        mycursor.execute("""
            SELECT c.id_commande, al.nom AS nom_livraison, al.rue AS rue_livraison,
                   al.code_postal AS cp_livraison, al.ville AS ville_livraison,
                   af.nom AS nom_facturation, af.rue AS rue_facturation,
                   af.code_postal AS cp_facturation, af.ville AS ville_facturation
            FROM commande c
            LEFT JOIN adresse al ON c.adresse_livraison_id=al.id_adresse
            LEFT JOIN adresse af ON c.adresse_facturation_id=af.id_adresse
            WHERE c.id_commande=%s AND c.utilisateur_id=%s
        """, (id_commande, id_client))
        commande_adresses = mycursor.fetchone()

    return render_template('client/commandes/show.html',
                           commande=commandes, cables_commande=cables_commande,
                           commande_adresses=commande_adresses)
