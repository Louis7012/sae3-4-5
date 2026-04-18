#! /usr/bin/python
# -*- coding:utf-8 -*-
import os
from random import random
from flask import Blueprint, request, render_template, redirect, flash
from connexion_db import get_db

admin_cable = Blueprint('admin_cable', __name__, template_folder='templates')


@admin_cable.route('/admin/cable/show')
def show_cable():
    mycursor = get_db().cursor()

    # Sélection de tous les câbles avec nb déclinaisons et stock minimum
    mycursor.execute("""
        SELECT c.id_cable, c.nom_cable, c.couleur, c.prix_cable, c.blindage,
               c.fournisseur, c.marque, c.photo, c.stock, c.type_prise_id,
               COUNT(dc.id_declinaison_cable) AS nb_declinaisons,
               MIN(dc.stock) AS min_stock
        FROM cable c
        LEFT JOIN declinaison_cable dc ON dc.cable_id = c.id_cable
        GROUP BY c.id_cable
        ORDER BY c.nom_cable
    """)
    cables = mycursor.fetchall()

    # Ajouter le nombre de commentaires non lus pour chaque câble
    for cable in cables:
        mycursor.execute("""
            SELECT COUNT(*) AS nb
            FROM commentaire
            WHERE cable_id = %s AND valider = 0 AND commentaire_parent_id IS NULL
        """, cable['id_cable'])
        row = mycursor.fetchone()
        cable['nb_commentaires_nouveaux'] = row['nb']

    return render_template('admin/cable/show_cable.html', cables=cables)


@admin_cable.route('/admin/cable/add', methods=['GET'])
def add_cable():
    mycursor = get_db().cursor()
    mycursor.execute("SELECT * FROM type_prise")
    types_prise = mycursor.fetchall()
    mycursor.execute("SELECT * FROM longueur")
    longueurs = mycursor.fetchall()
    return render_template('admin/cable/add_cable.html', types_prise=types_prise, longueurs=longueurs)


@admin_cable.route('/admin/cable/add', methods=['POST'])
def valid_add_cable():
    mycursor = get_db().cursor()
    nom = request.form.get('nom', '')
    type_prise_id = request.form.get('type_prise_id', '')
    longueur_id = request.form.get('longueur_id', '')
    prix = request.form.get('prix', '')
    blindage = request.form.get('blindage', '')
    fournisseur = request.form.get('fournisseur', '')
    marque = request.form.get('marque', '')
    stock = request.form.get('stock', 0)
    image = request.files.get('image', '')
    filename = None
    if image and image.filename:
        filename = 'img_upload' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    sql = """INSERT INTO cable(nom_cable, couleur, prix_cable, blindage, fournisseur, marque,
             photo, stock, type_prise_id, longueur_id)
             VALUES(%s, 'Noir', %s, %s, %s, %s, %s, %s, %s, %s)"""
    mycursor.execute(sql, (nom, prix, blindage, fournisseur, marque, filename, stock, type_prise_id, longueur_id))
    get_db().commit()
    flash('Câble ajouté', 'alert-success')
    return redirect('/admin/cable/show')


@admin_cable.route('/admin/cable/delete', methods=['GET'])
def delete_cable():
    id_cable = request.args.get('id_cable')
    mycursor = get_db().cursor()
    mycursor.execute("SELECT COUNT(*) AS nb FROM declinaison_cable WHERE cable_id = %s", id_cable)
    nb = mycursor.fetchone()['nb']
    if nb > 0:
        flash("Ce câble a des déclinaisons : supprimez-les d'abord.", 'alert-warning')
    else:
        mycursor.execute("SELECT photo FROM cable WHERE id_cable = %s", id_cable)
        cable = mycursor.fetchone()
        photo = cable['photo'] if cable else None
        mycursor.execute("DELETE FROM cable WHERE id_cable = %s", id_cable)
        get_db().commit()
        if photo and os.path.exists('static/images/' + photo):
            os.remove('static/images/' + photo)
        flash('Câble supprimé', 'alert-success')
    return redirect('/admin/cable/show')


@admin_cable.route('/admin/cable/edit', methods=['GET'])
def edit_cable():
    id_cable = request.args.get('id_cable')
    mycursor = get_db().cursor()
    mycursor.execute("SELECT * FROM cable WHERE id_cable = %s", id_cable)
    cable = mycursor.fetchone()
    mycursor.execute("SELECT * FROM type_prise")
    types_prise = mycursor.fetchall()
    mycursor.execute("SELECT * FROM longueur")
    longueurs = mycursor.fetchall()
    mycursor.execute("""
        SELECT dc.*, l.nom_longueur, c.nom_couleur, c.code_hex
        FROM declinaison_cable dc
        JOIN longueur l ON dc.longueur_id = l.id_longueur
        JOIN couleur c ON dc.couleur_id = c.id_couleur
        WHERE dc.cable_id = %s
    """, id_cable)
    declinaisons_cable = mycursor.fetchall()
    return render_template('admin/cable/edit_cable.html',
                           cable=cable, types_prise=types_prise,
                           longueurs=longueurs, declinaisons_cable=declinaisons_cable)


@admin_cable.route('/admin/cable/edit', methods=['POST'])
def valid_edit_cable():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_cable = request.form.get('id_cable')
    type_prise_id = request.form.get('type_prise_id', '')
    prix = request.form.get('prix', '')
    marque = request.form.get('marque', '')
    stock = request.form.get('stock', 0)
    image = request.files.get('image', '')
    mycursor.execute("SELECT photo FROM cable WHERE id_cable = %s", id_cable)
    row = mycursor.fetchone()
    image_nom = row['photo'] if row else None
    if image and image.filename:
        if image_nom and os.path.exists('static/images/' + image_nom):
            os.remove('static/images/' + image_nom)
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
        image_nom = filename
    mycursor.execute("""
        UPDATE cable SET nom_cable=%s, prix_cable=%s, photo=%s,
        type_prise_id=%s, marque=%s, stock=%s WHERE id_cable=%s
    """, (nom, prix, image_nom, type_prise_id, marque, stock, id_cable))
    get_db().commit()
    flash('Câble modifié', 'alert-success')
    return redirect('/admin/cable/show')
