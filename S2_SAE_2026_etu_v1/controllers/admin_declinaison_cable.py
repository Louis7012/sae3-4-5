#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_cable = Blueprint('admin_declinaison_cable', __name__,
                         template_folder='templates')


@admin_declinaison_cable.route('/admin/declinaison_cable/add')
def add_declinaison_cable():
    id_cable=request.args.get('id_cable')
    mycursor = get_db().cursor()
    cable=[]
    couleurs=None
    tailles=None
    d_taille_uniq=None
    d_couleur_uniq=None
    return render_template('admin/cable/add_declinaison_cable.html'
                           , cable=cable
                           , couleurs=couleurs
                           , tailles=tailles
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_cable.route('/admin/declinaison_cable/add', methods=['POST'])
def valid_add_declinaison_cable():
    mycursor = get_db().cursor()

    id_cable = request.form.get('id_cable')
    stock = request.form.get('stock')
    taille = request.form.get('taille')
    couleur = request.form.get('couleur')
    # attention au doublon
    get_db().commit()
    return redirect('/admin/cable/edit?id_cable=' + id_cable)


@admin_declinaison_cable.route('/admin/declinaison_cable/edit', methods=['GET'])
def edit_declinaison_cable():
    id_declinaison_cable = request.args.get('id_declinaison_cable')
    mycursor = get_db().cursor()
    declinaison_cable=[]
    couleurs=None
    tailles=None
    d_taille_uniq=None
    d_couleur_uniq=None
    return render_template('admin/cable/edit_declinaison_cable.html'
                           , tailles=tailles
                           , couleurs=couleurs
                           , declinaison_cable=declinaison_cable
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_cable.route('/admin/declinaison_cable/edit', methods=['POST'])
def valid_edit_declinaison_cable():
    id_declinaison_cable = request.form.get('id_declinaison_cable','')
    id_cable = request.form.get('id_cable','')
    stock = request.form.get('stock','')
    taille_id = request.form.get('id_taille','')
    couleur_id = request.form.get('id_couleur','')
    mycursor = get_db().cursor()

    message = u'declinaison_cable modifié , id:' + str(id_declinaison_cable) + '- stock :' + str(stock) + ' - taille_id:' + str(taille_id) + ' - couleur_id:' + str(couleur_id)
    flash(message, 'alert-success')
    return redirect('/admin/cable/edit?id_cable=' + str(id_cable))


@admin_declinaison_cable.route('/admin/declinaison_cable/delete', methods=['GET'])
def admin_delete_declinaison_cable():
    id_declinaison_cable = request.args.get('id_declinaison_cable','')
    id_cable = request.args.get('id_cable','')

    flash(u'declinaison supprimée, id_declinaison_cable : ' + str(id_declinaison_cable),  'alert-success')
    return redirect('/admin/cable/edit?id_cable=' + str(id_cable))
