#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__, template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("SELECT * FROM utilisateur WHERE id_utilisateur=%s", id_client)
    utilisateur = mycursor.fetchone()
    mycursor.execute("""
        SELECT a.*, COUNT(DISTINCT c.id_commande) AS nb_commandes
        FROM adresse a
        LEFT JOIN commande c ON c.adresse_livraison_id=a.id_adresse OR c.adresse_facturation_id=a.id_adresse
        WHERE a.utilisateur_id=%s
        GROUP BY a.id_adresse
        ORDER BY a.est_favorite DESC, a.est_valide DESC
    """, id_client)
    adresses = mycursor.fetchall()
    mycursor.execute("SELECT COUNT(*) AS total, SUM(est_valide) AS valides FROM adresse WHERE utilisateur_id=%s", id_client)
    nb_adresses = mycursor.fetchone()
    return render_template('client/coordonnee/show_coordonnee.html',
                           utilisateur=utilisateur, adresses=adresses, nb_adresses=nb_adresses)


@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("SELECT * FROM utilisateur WHERE id_utilisateur=%s", id_client)
    utilisateur = mycursor.fetchone()
    return render_template('client/coordonnee/edit_coordonnee.html', utilisateur=utilisateur)


@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')
    # Vérifier doublon login/email
    mycursor.execute("SELECT id_utilisateur FROM utilisateur WHERE (login=%s OR email=%s) AND id_utilisateur!=%s",
                     (login, email, id_client))
    doublon = mycursor.fetchone()
    if doublon:
        flash("Cet email ou ce login est déjà utilisé par un autre compte.", 'alert-warning')
        return redirect('/client/coordonnee/edit')
    mycursor.execute("UPDATE utilisateur SET nom=%s, login=%s, email=%s WHERE id_utilisateur=%s",
                     (nom, login, email, id_client))
    get_db().commit()
    session['login'] = login
    flash("Coordonnées mises à jour", 'alert-success')
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    return render_template('client/coordonnee/add_adresse.html')


@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal', '')
    ville = request.form.get('ville')

    # Vérification code postal (5 chiffres) côté serveur
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash("Le code postal doit être composé de 5 chiffres.", 'alert-danger')
        return render_template('client/coordonnee/add_adresse.html',
                               nom=nom, rue=rue, code_postal=code_postal, ville=ville)

    # Max 4 adresses valides
    mycursor.execute("SELECT COUNT(*) AS nb FROM adresse WHERE utilisateur_id=%s AND est_valide=1", id_client)
    if mycursor.fetchone()['nb'] >= 4:
        flash("⚠️ Vous avez atteint le maximum de 4 adresses valides.", 'alert-warning')
        return redirect('/client/coordonnee/show')

    # La nouvelle adresse devient favorite
    mycursor.execute("UPDATE adresse SET est_favorite=0 WHERE utilisateur_id=%s", id_client)
    mycursor.execute("INSERT INTO adresse(utilisateur_id, nom, rue, code_postal, ville, est_favorite, est_valide) VALUES(%s,%s,%s,%s,%s,1,1)",
                     (id_client, nom, rue, code_postal, ville))
    get_db().commit()
    flash("Adresse ajoutée", 'alert-success')
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse', methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')

    # Vérifier que l'adresse appartient bien à cet utilisateur
    mycursor.execute("SELECT * FROM adresse WHERE id_adresse=%s AND utilisateur_id=%s", (id_adresse, id_client))
    adresse = mycursor.fetchone()
    if not adresse:
        flash("⚠️ Vous n'êtes pas autorisé à supprimer cette adresse.", 'alert-warning')
        return redirect('/client/coordonnee/show')

    # Vérifier si utilisée dans une commande
    mycursor.execute("SELECT COUNT(*) AS nb FROM commande WHERE adresse_livraison_id=%s OR adresse_facturation_id=%s",
                     (id_adresse, id_adresse))
    nb = mycursor.fetchone()['nb']
    if nb > 0:
        # Marquer non valide au lieu de supprimer
        mycursor.execute("UPDATE adresse SET est_valide=0, est_favorite=0 WHERE id_adresse=%s", id_adresse)
        # Si c'était la favorite, trouver la dernière adresse utilisée valide
        if adresse['est_favorite']:
            mycursor.execute("""SELECT a.id_adresse FROM adresse a
                                JOIN commande c ON c.adresse_livraison_id=a.id_adresse
                                WHERE a.utilisateur_id=%s AND a.est_valide=1
                                ORDER BY c.date_achat DESC LIMIT 1""", id_client)
            new_fav = mycursor.fetchone()
            if new_fav:
                mycursor.execute("UPDATE adresse SET est_favorite=1 WHERE id_adresse=%s", new_fav['id_adresse'])
    else:
        est_favorite = adresse['est_favorite']
        mycursor.execute("DELETE FROM adresse WHERE id_adresse=%s", id_adresse)
        if est_favorite:
            mycursor.execute("""SELECT id_adresse FROM adresse WHERE utilisateur_id=%s AND est_valide=1
                                ORDER BY id_adresse DESC LIMIT 1""", id_client)
            new_fav = mycursor.fetchone()
            if new_fav:
                mycursor.execute("UPDATE adresse SET est_favorite=1 WHERE id_adresse=%s", new_fav['id_adresse'])

    get_db().commit()
    flash("Adresse supprimée", 'alert-success')
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')
    mycursor.execute("SELECT * FROM adresse WHERE id_adresse=%s AND utilisateur_id=%s", (id_adresse, id_client))
    adresse = mycursor.fetchone()
    if not adresse:
        flash("⚠️ Adresse introuvable.", 'alert-warning')
        return redirect('/client/coordonnee/show')
    return render_template('client/coordonnee/edit_adresse.html', adresse=adresse)


@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal', '')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')

    # Vérifier appartenance
    mycursor.execute("SELECT * FROM adresse WHERE id_adresse=%s AND utilisateur_id=%s", (id_adresse, id_client))
    adresse = mycursor.fetchone()
    if not adresse:
        flash("⚠️ Vous n'êtes pas autorisé à modifier cette adresse.", 'alert-warning')
        return redirect('/client/coordonnee/show')

    # Vérification code postal
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash("Le code postal doit être composé de 5 chiffres.", 'alert-danger')
        return render_template('client/coordonnee/edit_adresse.html',
                               adresse={'id_adresse': id_adresse, 'nom': nom, 'rue': rue,
                                        'code_postal': code_postal, 'ville': ville})

    # Vérifier si utilisée dans commande
    mycursor.execute("SELECT COUNT(*) AS nb FROM commande WHERE adresse_livraison_id=%s OR adresse_facturation_id=%s",
                     (id_adresse, id_adresse))
    nb = mycursor.fetchone()['nb']

    if nb > 0:
        # Marquer l'ancienne non valide et créer une nouvelle
        mycursor.execute("UPDATE adresse SET est_valide=0, est_favorite=0 WHERE id_adresse=%s", id_adresse)
        # Vérifier quota
        mycursor.execute("SELECT COUNT(*) AS nb FROM adresse WHERE utilisateur_id=%s AND est_valide=1", id_client)
        if mycursor.fetchone()['nb'] >= 4:
            flash("⚠️ Maximum de 4 adresses valides atteint.", 'alert-warning')
            mycursor.execute("UPDATE adresse SET est_valide=1 WHERE id_adresse=%s", id_adresse)  # annuler
            get_db().commit()
            return redirect('/client/coordonnee/show')
        was_favorite = adresse['est_favorite']
        mycursor.execute("INSERT INTO adresse(utilisateur_id, nom, rue, code_postal, ville, est_favorite, est_valide) VALUES(%s,%s,%s,%s,%s,%s,1)",
                         (id_client, nom, rue, code_postal, ville, was_favorite))
    else:
        mycursor.execute("UPDATE adresse SET nom=%s, rue=%s, code_postal=%s, ville=%s WHERE id_adresse=%s",
                         (nom, rue, code_postal, ville, id_adresse))
        # Si c'était la favorite, elle le reste

    get_db().commit()
    flash("Adresse modifiée", 'alert-success')
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/set_favorite', methods=['POST'])
def client_coordonnee_set_favorite():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')
    mycursor.execute("SELECT id_adresse FROM adresse WHERE id_adresse=%s AND utilisateur_id=%s", (id_adresse, id_client))
    if not mycursor.fetchone():
        flash("⚠️ Non autorisé.", 'alert-warning')
        return redirect('/client/coordonnee/show')
    mycursor.execute("UPDATE adresse SET est_favorite=0 WHERE utilisateur_id=%s", id_client)
    mycursor.execute("UPDATE adresse SET est_favorite=1 WHERE id_adresse=%s", id_adresse)
    get_db().commit()
    return redirect('/client/coordonnee/show')
