#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                        template_folder='templates')


@admin_commentaire.route('/admin/cable/commentaires', methods=['GET'])
def admin_cable_details():
    mycursor = get_db().cursor()
    id_cable =  request.args.get('id_cable', None)
    sql = '''    requête admin_type_cable_1    '''
    commentaires = {}
    sql = '''   requête admin_type_cable_1_bis   '''
    cable = []
    sql = '''   requête admin_type_cable_1_3   '''
    nb_commentaires = []
    return render_template('admin/cable/show_cable_commentaires.html'
                           , commentaires=commentaires
                           , cable=cable
                           , nb_commentaires=nb_commentaires
                           )

@admin_commentaire.route('/admin/cable/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_utilisateur = request.form.get('id_utilisateur', None)
    id_cable = request.form.get('id_cable', None)
    date_publication = request.form.get('date_publication', None)
    sql = '''    requête admin_type_cable_2   '''
    tuple_delete=(id_utilisateur,id_cable,date_publication)
    get_db().commit()
    return redirect('/admin/cable/commentaires?id_cable='+id_cable)


@admin_commentaire.route('/admin/cable/commentaires/repondre', methods=['POST','GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_utilisateur = request.args.get('id_utilisateur', None)
        id_cable = request.args.get('id_cable', None)
        date_publication = request.args.get('date_publication', None)
        return render_template('admin/cable/add_commentaire.html',id_utilisateur=id_utilisateur,id_cable=id_cable,date_publication=date_publication )

    mycursor = get_db().cursor()
    id_utilisateur = session['id_user']   #1 admin
    id_cable = request.form.get('id_cable', None)
    date_publication = request.form.get('date_publication', None)
    commentaire = request.form.get('commentaire', None)
    sql = '''    requête admin_type_prise_3   '''
    get_db().commit()
    return redirect('/admin/cable/commentaires?id_cable='+id_cable)


@admin_commentaire.route('/admin/cable/commentaires/valider', methods=['POST','GET'])
def admin_comment_valider():
    id_cable = request.args.get('id_cable', None)
    mycursor = get_db().cursor()
    sql = '''   requête admin_type_prise_4   '''
    get_db().commit()
    return redirect('/admin/cable/commentaires?id_cable='+id_cable)