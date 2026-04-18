#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_cable = Blueprint('admin_declinaison_cable', __name__, template_folder='templates')


def maj_stock_cable(mycursor, id_cable):
    """Calcule le stock total des déclinaisons et met à jour la table cable."""
    mycursor.execute("SELECT SUM(stock) AS total FROM declinaison_cable WHERE cable_id=%s", id_cable)
    row = mycursor.fetchone()
    nouveau_stock = row['total'] if row['total'] else 0
    mycursor.execute("UPDATE cable SET stock=%s WHERE id_cable=%s", (nouveau_stock, id_cable))


@admin_declinaison_cable.route('/admin/declinaison_cable/add')
def add_declinaison_cable():
    id_cable = request.args.get('id_cable')
    mycursor = get_db().cursor()
    sql = "SELECT * FROM cable WHERE id_cable=%s"
    mycursor.execute(sql, id_cable)
    cable = mycursor.fetchone()
    sql = "SELECT * FROM longueur"
    mycursor.execute(sql)
    longueurs = mycursor.fetchall()
    sql = "SELECT * FROM couleur"
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()
    # Vérifier si taille unique déjà sélectionnée (couleur_id=1)
    sql = "SELECT COUNT(*) as nb FROM declinaison_cable WHERE cable_id=%s AND couleur_id=1"
    mycursor.execute(sql, id_cable)
    d_unique = mycursor.fetchone()['nb'] > 0
    return render_template('admin/cable/add_declinaison_cable.html',
                           cable=cable, longueurs=longueurs, couleurs=couleurs, d_unique=d_unique)


@admin_declinaison_cable.route('/admin/declinaison_cable/add', methods=['POST'])
def valid_add_declinaison_cable():
    mycursor = get_db().cursor()
    id_cable = request.form.get('id_cable')
    stock = request.form.get('stock', 0)
    prix = request.form.get('prix', 0)
    longueur_id = request.form.get('longueur_id')
    couleur_id = request.form.get('couleur_id')

    # Si couleur unique (id=1), pas d'autre déclinaison possible
    sql = "SELECT COUNT(*) as nb FROM declinaison_cable WHERE cable_id=%s AND couleur_id != 1"
    mycursor.execute(sql, id_cable)
    nb_autres = mycursor.fetchone()['nb']
    if couleur_id == '1' and nb_autres > 0:
        flash("Impossible d'ajouter 'unique' quand d'autres déclinaisons existent.", 'alert-warning')
        return redirect('/admin/cable/edit?id_cable=' + id_cable)

    sql = "SELECT COUNT(*) as nb FROM declinaison_cable WHERE cable_id=%s AND couleur_id=1"
    mycursor.execute(sql, id_cable)
    if mycursor.fetchone()['nb'] > 0 and couleur_id != '1':
        flash("Impossible d'ajouter une déclinaison quand 'unique' est déjà sélectionnée.", 'alert-warning')
        return redirect('/admin/cable/edit?id_cable=' + id_cable)

    # Vérifier doublon
    sql = "SELECT COUNT(*) as nb FROM declinaison_cable WHERE cable_id=%s AND longueur_id=%s AND couleur_id=%s"
    mycursor.execute(sql, (id_cable, longueur_id, couleur_id))
    if mycursor.fetchone()['nb'] > 0:
        flash("Cette déclinaison existe déjà.", 'alert-warning')
        return redirect('/admin/cable/edit?id_cable=' + id_cable)

    sql = "INSERT INTO declinaison_cable(cable_id, longueur_id, couleur_id, stock, prix) VALUES(%s,%s,%s,%s,%s)"
    mycursor.execute(sql, (id_cable, longueur_id, couleur_id, stock, prix))
    # MAJ stock du câble
    maj_stock_cable(mycursor, id_cable)
    get_db().commit()
    flash('Déclinaison ajoutée avec succès', 'alert-success')
    return redirect('/admin/cable/edit?id_cable=' + id_cable)


@admin_declinaison_cable.route('/admin/declinaison_cable/edit', methods=['GET'])
def edit_declinaison_cable():
    id_declinaison_cable = request.args.get('id_declinaison_cable')
    mycursor = get_db().cursor()
    sql = """SELECT dc.*, l.nom_longueur, c.nom_couleur 
             FROM declinaison_cable dc 
             JOIN longueur l ON dc.longueur_id=l.id_longueur 
             JOIN couleur c ON dc.couleur_id=c.id_couleur
             WHERE dc.id_declinaison_cable=%s"""
    mycursor.execute(sql, id_declinaison_cable)
    declinaison_cable = mycursor.fetchone()
    sql = "SELECT * FROM longueur"
    mycursor.execute(sql)
    longueurs = mycursor.fetchall()
    sql = "SELECT * FROM couleur"
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()
    return render_template('admin/cable/edit_declinaison_cable.html',
                           declinaison_cable=declinaison_cable, longueurs=longueurs, couleurs=couleurs)


@admin_declinaison_cable.route('/admin/declinaison_cable/edit', methods=['POST'])
def valid_edit_declinaison_cable():
    id_declinaison_cable = request.form.get('id_declinaison_cable', '')
    id_cable = request.form.get('id_cable', '')
    stock = request.form.get('stock', '')
    prix = request.form.get('prix', '')
    longueur_id = request.form.get('longueur_id', '')
    couleur_id = request.form.get('couleur_id', '')
    mycursor = get_db().cursor()

    # Vérifier si déjà commandée
    sql = """SELECT COUNT(*) as nb FROM ligne_commande WHERE declinaison_cable_id=%s"""
    mycursor.execute(sql, id_declinaison_cable)
    nb_cmd = mycursor.fetchone()['nb']

    if nb_cmd > 0:
        # Conserver ancienne déclinaison comme non valide (copie)
        sql = """INSERT INTO declinaison_cable(cable_id, longueur_id, couleur_id, stock, prix) 
                 SELECT cable_id, longueur_id, couleur_id, 0, prix FROM declinaison_cable WHERE id_declinaison_cable=%s"""
        mycursor.execute(sql, id_declinaison_cable)
        # Mettre l'ancienne à stock 0 (garder pour les factures)
        flash("La déclinaison a déjà été commandée. Une copie a été créée.", 'alert-info')

    sql = "UPDATE declinaison_cable SET longueur_id=%s, couleur_id=%s, stock=%s, prix=%s WHERE id_declinaison_cable=%s"
    mycursor.execute(sql, (longueur_id, couleur_id, stock, prix, id_declinaison_cable))
    # MAJ stock câble
    maj_stock_cable(mycursor, id_cable)
    get_db().commit()
    flash('Déclinaison modifiée', 'alert-success')
    return redirect('/admin/cable/edit?id_cable=' + str(id_cable))


@admin_declinaison_cable.route('/admin/declinaison_cable/delete', methods=['GET'])
def admin_delete_declinaison_cable():
    id_declinaison_cable = request.args.get('id_declinaison_cable', '')
    id_cable = request.args.get('id_cable', '')
    mycursor = get_db().cursor()

    # Vérifier si déjà commandée
    sql = "SELECT COUNT(*) as nb FROM ligne_commande WHERE declinaison_cable_id=%s"
    mycursor.execute(sql, id_declinaison_cable)
    nb = mycursor.fetchone()['nb']
    if nb > 0:
        flash("Impossible de supprimer une déclinaison déjà commandée.", 'alert-warning')
    else:
        sql = "DELETE FROM declinaison_cable WHERE id_declinaison_cable=%s"
        mycursor.execute(sql, id_declinaison_cable)
        # Calculer le stock total des déclinaisons en Python
        mycursor.execute("SELECT SUM(stock) AS total FROM declinaison_cable WHERE cable_id=%s", id_cable)
        row = mycursor.fetchone()
        nouveau_stock = row['total'] if row['total'] else 0
        mycursor.execute("UPDATE cable SET stock=%s WHERE id_cable=%s", (nouveau_stock, id_cable))
        get_db().commit()
        flash('Déclinaison supprimée', 'alert-success')
    return redirect('/admin/cable/edit?id_cable=' + str(id_cable))
