#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__, template_folder='templates')


@admin_commentaire.route('/admin/cable/commentaires', methods=['GET'])
def admin_cable_details():
    mycursor = get_db().cursor()
    id_cable = request.args.get('id_cable', None)

    # Informations du câble avec note moyenne
    mycursor.execute("""
        SELECT c.id_cable, c.nom_cable AS nom, c.photo AS image,
               AVG(a.note) AS moyenne_notes, COUNT(a.id_avis) AS nb_notes
        FROM cable c
        LEFT JOIN avis a ON a.cable_id = c.id_cable
        WHERE c.id_cable = %s
        GROUP BY c.id_cable
    """, id_cable)
    cable = mycursor.fetchone()

    # Commentaires triés : non validés d'abord, puis validés, réponses sous leur parent
    mycursor.execute("""
        SELECT com.id_commentaire, com.commentaire, com.date_publication,
               com.valider, com.commentaire_parent_id, com.utilisateur_id,
               u.login AS nom
        FROM commentaire com
        JOIN utilisateur u ON com.utilisateur_id = u.id_utilisateur
        WHERE com.cable_id = %s
        ORDER BY com.valider ASC, com.date_publication DESC
    """, id_cable)
    commentaires = mycursor.fetchall()

    # Statistiques : 3 requêtes simples séparées
    mycursor.execute("""
        SELECT COUNT(*) AS nb FROM commentaire
        WHERE cable_id = %s AND commentaire_parent_id IS NULL
    """, id_cable)
    nb_total = mycursor.fetchone()['nb']

    mycursor.execute("""
        SELECT COUNT(*) AS nb FROM commentaire
        WHERE cable_id = %s AND valider = 0 AND commentaire_parent_id IS NULL
    """, id_cable)
    nb_nouveaux = mycursor.fetchone()['nb']

    mycursor.execute("""
        SELECT COUNT(*) AS nb FROM commentaire
        WHERE cable_id = %s AND valider = 1 AND commentaire_parent_id IS NULL
    """, id_cable)
    nb_valides = mycursor.fetchone()['nb']

    nb_commentaires = {
        'nb_commentaires_total': nb_total,
        'nb_commentaires_nouveaux': nb_nouveaux,
        'nb_commentaires_valider': nb_valides
    }

    return render_template('admin/cable/show_article_commentaires.html',
                           commentaires=commentaires, article=cable,
                           nb_commentaires=nb_commentaires)


@admin_commentaire.route('/admin/cable/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_commentaire = request.form.get('id_commentaire', None)
    id_cable = request.form.get('id_cable', None)
    # Supprimer les réponses éventuelles puis le commentaire
    mycursor.execute("DELETE FROM commentaire WHERE commentaire_parent_id = %s", id_commentaire)
    mycursor.execute("DELETE FROM commentaire WHERE id_commentaire = %s", id_commentaire)
    get_db().commit()
    return redirect('/admin/cable/commentaires?id_cable=' + id_cable)


@admin_commentaire.route('/admin/cable/commentaires/repondre', methods=['POST', 'GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_commentaire = request.args.get('id_commentaire', None)
        id_cable = request.args.get('id_cable', None)
        return render_template('admin/cable/add_commentaire.html',
                               id_commentaire=id_commentaire, id_cable=id_cable)
    mycursor = get_db().cursor()
    id_admin = session['id_user']
    id_cable = request.form.get('id_cable', None)
    id_commentaire_parent = request.form.get('id_commentaire', None)
    commentaire = request.form.get('commentaire', None)
    mycursor.execute("""
        INSERT INTO commentaire(utilisateur_id, cable_id, commentaire, valider, commentaire_parent_id)
        VALUES(%s, %s, %s, 1, %s)
    """, (id_admin, id_cable, commentaire, id_commentaire_parent))
    get_db().commit()
    return redirect('/admin/cable/commentaires?id_cable=' + id_cable)


@admin_commentaire.route('/admin/cable/commentaires/valider', methods=['GET'])
def admin_comment_valider():
    id_cable = request.args.get('id_cable', None)
    mycursor = get_db().cursor()
    mycursor.execute("""
        UPDATE commentaire SET valider = 1
        WHERE cable_id = %s AND commentaire_parent_id IS NULL
    """, id_cable)
    get_db().commit()
    flash("Commentaires validés", "alert-success")
    return redirect('/admin/cable/commentaires?id_cable=' + id_cable)
