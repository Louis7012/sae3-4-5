#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session, abort
from connexion_db import get_db
from controllers.client_liste_envies import client_historique_add

client_commentaire = Blueprint('client_commentaire', __name__, template_folder='templates')


@client_commentaire.route('/client/cable/details', methods=['GET'])
def client_cable_details():
    mycursor = get_db().cursor()
    id_cable = request.args.get('id_cable', None)
    id_client = session['id_user']

    # Historique
    client_historique_add(id_cable, id_client)

    mycursor.execute("""SELECT c.id_cable, c.nom_cable AS nom, c.photo AS image, c.prix_cable AS prix,
                               AVG(a.note) AS moyenne_notes, COUNT(a.id_avis) AS nb_notes
                        FROM cable c LEFT JOIN avis a ON a.cable_id=c.id_cable
                        WHERE c.id_cable=%s GROUP BY c.id_cable""", id_cable)
    cable = mycursor.fetchone()
    if not cable:
        abort(404, "Câble introuvable")

    # Vérifier si le client a acheté ce câble
    mycursor.execute("""SELECT SUM(lc.quantite_commande) AS nb_commandes_cable
                        FROM ligne_commande lc
                        JOIN commande co ON lc.commande_id=co.id_commande
                        WHERE co.utilisateur_id=%s AND lc.cable_id=%s""", (id_client, id_cable))
    commandes_cables = mycursor.fetchone()

    # Note de l'utilisateur
    mycursor.execute("SELECT note FROM avis WHERE utilisateur_id=%s AND cable_id=%s", (id_client, id_cable))
    note_row = mycursor.fetchone()
    note = note_row['note'] if note_row else None

    # Commentaires ordonnés (non validés d'abord, puis validés, réponses après leurs parents)
    mycursor.execute("""SELECT com.*, u.login AS nom, u.id_utilisateur
                        FROM commentaire com JOIN utilisateur u ON com.utilisateur_id=u.id_utilisateur
                        WHERE com.cable_id=%s
                        ORDER BY com.valider ASC, com.commentaire_parent_id ASC, com.date_publication DESC""", id_cable)
    commentaires = mycursor.fetchall()

    # Statistiques commentaires : 4 requêtes simples
    mycursor.execute("""SELECT COUNT(*) AS nb FROM commentaire
        WHERE cable_id=%s AND commentaire_parent_id IS NULL""", id_cable)
    nb_total = mycursor.fetchone()['nb']

    mycursor.execute("""SELECT COUNT(*) AS nb FROM commentaire
        WHERE cable_id=%s AND utilisateur_id=%s AND commentaire_parent_id IS NULL""",
        (id_cable, id_client))
    nb_utilisateur = mycursor.fetchone()['nb']

    mycursor.execute("""SELECT COUNT(*) AS nb FROM commentaire
        WHERE cable_id=%s AND valider=1 AND commentaire_parent_id IS NULL""", id_cable)
    nb_total_valide = mycursor.fetchone()['nb']

    mycursor.execute("""SELECT COUNT(*) AS nb FROM commentaire
        WHERE cable_id=%s AND utilisateur_id=%s AND valider=1 AND commentaire_parent_id IS NULL""",
        (id_cable, id_client))
    nb_utilisateur_valide = mycursor.fetchone()['nb']

    nb_commentaires = {
        'nb_commentaires_total': nb_total,
        'nb_commentaires_utilisateur': nb_utilisateur,
        'nb_commentaires_total_valide': nb_total_valide,
        'nb_commentaires_utilisateur_valide': nb_utilisateur_valide
    }

    return render_template('client/cable_info/article_details.html',
                           cable=cable, commentaires=commentaires,
                           commandes_cables=commandes_cables, note=note,
                           nb_commentaires=nb_commentaires)


@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    commentaire = request.form.get('commentaire', None)
    id_client = session['id_user']
    id_cable = request.form.get('id_cable', None)

    if not commentaire or commentaire == '':
        flash('Commentaire vide non pris en compte', 'alert-warning')
        return redirect('/client/cable/details?id_cable=' + id_cable)
    if len(commentaire) < 3:
        flash('Commentaire trop court (3 caractères minimum)', 'alert-warning')
        return redirect('/client/cable/details?id_cable=' + id_cable)

    # Vérifier quota (max 3 par article)
    mycursor.execute("""SELECT COUNT(*) AS nb FROM commentaire
                        WHERE utilisateur_id=%s AND cable_id=%s AND commentaire_parent_id IS NULL""",
                     (id_client, id_cable))
    nb = mycursor.fetchone()['nb']
    if nb >= 3:
        flash('⚠️ Quota atteint : vous ne pouvez pas poster plus de 3 commentaires sur ce câble.', 'alert-danger')
        return redirect('/client/cable/details?id_cable=' + id_cable)

    # Vérifier que le client a acheté ce câble
    mycursor.execute("""SELECT COUNT(*) AS nb FROM ligne_commande lc
                        JOIN commande c ON lc.commande_id=c.id_commande
                        WHERE c.utilisateur_id=%s AND lc.cable_id=%s""", (id_client, id_cable))
    if mycursor.fetchone()['nb'] == 0:
        flash("Seuls les clients ayant acheté ce câble peuvent commenter.", 'alert-warning')
        return redirect('/client/cable/details?id_cable=' + id_cable)

    mycursor.execute("INSERT INTO commentaire(commentaire, utilisateur_id, cable_id) VALUES(%s,%s,%s)",
                     (commentaire, id_client, id_cable))
    get_db().commit()
    return redirect('/client/cable/details?id_cable=' + id_cable)


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_detete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.form.get('id_cable', None)
    id_commentaire = request.form.get('id_commentaire', None)
    mycursor.execute("DELETE FROM commentaire WHERE id_commentaire=%s AND utilisateur_id=%s",
                     (id_commentaire, id_client))
    get_db().commit()
    return redirect('/client/cable/details?id_cable=' + id_cable)


@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_cable = request.form.get('id_cable', None)
    # Vérifier si une note existe déjà pour ce client/câble
    mycursor.execute("SELECT id_avis FROM avis WHERE utilisateur_id=%s AND cable_id=%s",
                     (id_client, id_cable))
    avis_existant = mycursor.fetchone()
    if avis_existant:
        mycursor.execute("UPDATE avis SET note=%s WHERE utilisateur_id=%s AND cable_id=%s",
                         (note, id_client, id_cable))
    else:
        mycursor.execute("INSERT INTO avis(note, utilisateur_id, cable_id) VALUES(%s,%s,%s)",
                         (note, id_client, id_cable))
    get_db().commit()
    return redirect('/client/cable/details?id_cable=' + id_cable)


@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_cable = request.form.get('id_cable', None)
    mycursor.execute("UPDATE avis SET note=%s WHERE utilisateur_id=%s AND cable_id=%s",
                     (note, id_client, id_cable))
    get_db().commit()
    return redirect('/client/cable/details?id_cable=' + id_cable)


@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.form.get('id_cable', None)
    mycursor.execute("DELETE FROM avis WHERE utilisateur_id=%s AND cable_id=%s", (id_client, id_cable))
    get_db().commit()
    return redirect('/client/cable/details?id_cable=' + id_cable)
