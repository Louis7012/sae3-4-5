#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash
from connexion_db import get_db

admin_type_prise = Blueprint('admin_type_prise', __name__, template_folder='templates')


@admin_type_prise.route('/admin/type_prise/show')
def show_type_prise():
    mycursor = get_db().cursor()
    mycursor.execute("""
        SELECT tp.id_type_prise, tp.nom_type_prise,
               COUNT(c.id_cable) AS nb_cables
        FROM type_prise tp
        LEFT JOIN cable c ON c.type_prise_id=tp.id_type_prise
        GROUP BY tp.id_type_prise
        ORDER BY tp.nom_type_prise
    """)
    types_prise = mycursor.fetchall()
    return render_template('admin/type_prise/show_type_article.html', types_article=types_prise)


@admin_type_prise.route('/admin/type_prise/add', methods=['GET'])
def add_type_prise():
    return render_template('admin/type_prise/add_type_article.html')


@admin_type_prise.route('/admin/type_prise/add', methods=['POST'])
def valid_add_type_prise():
    libelle = request.form.get('libelle', '')
    mycursor = get_db().cursor()
    mycursor.execute("INSERT INTO type_prise(nom_type_prise) VALUES(%s)", (libelle,))
    get_db().commit()
    flash('Type de prise ajouté : ' + libelle, 'alert-success')
    return redirect('/admin/type_prise/show')


@admin_type_prise.route('/admin/type_prise/delete', methods=['GET'])
def delete_type_prise():
    id_type_prise = request.args.get('id_type_prise', '')
    mycursor = get_db().cursor()
    mycursor.execute("SELECT COUNT(*) AS nb FROM cable WHERE type_prise_id=%s", id_type_prise)
    nb = mycursor.fetchone()['nb']
    if nb > 0:
        flash("Impossible de supprimer : des câbles utilisent ce type.", 'alert-warning')
    else:
        mycursor.execute("DELETE FROM type_prise WHERE id_type_prise=%s", id_type_prise)
        get_db().commit()
        flash('Type supprimé', 'alert-success')
    return redirect('/admin/type_prise/show')


@admin_type_prise.route('/admin/type_prise/edit', methods=['GET'])
def edit_type_prise():
    id_type_prise = request.args.get('id_type_prise', '')
    mycursor = get_db().cursor()
    mycursor.execute("SELECT * FROM type_prise WHERE id_type_prise=%s", id_type_prise)
    type_prise = mycursor.fetchone()
    return render_template('admin/type_prise/edit_type_article.html', type_article=type_prise)


@admin_type_prise.route('/admin/type_prise/edit', methods=['POST'])
def valid_edit_type_prise():
    libelle = request.form.get('libelle', '')
    id_type_prise = request.form.get('id_type_prise', '')
    mycursor = get_db().cursor()
    mycursor.execute("UPDATE type_prise SET nom_type_prise=%s WHERE id_type_prise=%s", (libelle, id_type_prise))
    get_db().commit()
    flash('Type modifié : ' + libelle, 'alert-success')
    return redirect('/admin/type_prise/show')
