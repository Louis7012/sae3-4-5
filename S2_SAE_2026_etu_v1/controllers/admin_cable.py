#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_cable = Blueprint('admin_cable', __name__,
                          template_folder='templates')


@admin_cable.route('/admin/cable/show')
def show_cable():
    mycursor = get_db().cursor()
    sql = "SELECT id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, marque, photo, stock, type_prise_id, longueur_id FROM cable;"
    mycursor.execute(sql)
    cables = mycursor.fetchall()
    return render_template('admin/cable/show_cable.html', cable=cables)


@admin_cable.route('/admin/cable/add', methods=['GET'])
def add_cable():
    mycursor = get_db().cursor()

    return render_template('admin/cable/add_cable.html'
                           #,types_article=type_article,
                           #,couleurs=colors
                           #,tailles=tailles
                            )


@admin_cable.route('/admin/cable/add', methods=['POST'])
def valid_add_cable():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_prise_id = request.form.get('type_prise_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    sql = '''  requête admin_cable_2 '''

    tuple_add = (nom, filename, prix, type_prise_id, description)
    print(tuple_add)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'cable ajouté , nom: ', nom, ' - type_prise:', type_prise_id, ' - prix:', prix,
          ' - description:', description, ' - image:', image)
    message = u'cable ajouté , nom:' + nom + '- type_prise :' + type_prise_id + ' - prix:' + prix + ' - description:' + description + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/cable/show')


@admin_cable.route('/admin/cable/delete', methods=['GET'])
def delete_cable():
    id_cable=request.args.get('id_cable')
    mycursor = get_db().cursor()
    sql = ''' requête admin_cable_3 '''
    mycursor.execute(sql, id_cable)
    nb_declinaison = mycursor.fetchone()
    if nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans ce cable : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' requête admin_cable_4 '''
        mycursor.execute(sql, id_cable)
        cable = mycursor.fetchone()
        print(cable)
        image = cable['image']

        sql = ''' requête admin_cable_5  '''
        mycursor.execute(sql, id_cable)
        get_db().commit()
        if image != None:
            os.remove('static/images/' + image)

        print("un cable supprimé, id :", id_cable)
        message = u'un cable supprimé, id : ' + id_cable
        flash(message, 'alert-success')

    return redirect('/admin/cable/show')


@admin_cable.route('/admin/cable/edit', methods=['GET'])
def edit_cable():
    id_cable=request.args.get('id_cable')
    mycursor = get_db().cursor()
    sql =  "SELECT id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, marque, photo, stock, type_prise_id, longueur_id FROM cable WHERE id_cable = %s;"
    mycursor.execute(sql, id_cable)
    cable = mycursor.fetchone()
    print(cable)
    sql = "SELECT * FROM type_prise;"
    mycursor.execute(sql)
    types_prise = mycursor.fetchall()

    # sql = '''
    # requête admin_cable_6
    # '''
    # mycursor.execute(sql, id_cable)
    # declinaisons_cable = mycursor.fetchall()

    return render_template('admin/cable/edit_cable.html'
                           ,cable=cable
                           ,types_prise=types_prise
                         #  ,declinaisons_cable=declinaisons_cable
                           )


@admin_cable.route('/admin/cable/edit', methods=['POST'])
def valid_edit_cable():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_cable = request.form.get('id_cable')
    image = request.files.get('image', '')
    type_prise_id = request.form.get('type_prise_id', '')
    prix = request.form.get('prix', '')
    marque = request.form.get('marque')
    stock = request.form.get('stock')
    sql = "SELECT photo FROM cable WHERE id_cable=%s;"
    mycursor.execute(sql, id_cable)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename

    sql = "UPDATE cable SET nom_cable=%s, prix_cable=%s, photo=%s, type_prise_id=%s, marque=%s, stock=%s WHERE id_cable = %s;"
    mycursor.execute(sql, (nom, prix, image_nom, type_prise_id, marque, stock, id_cable))

    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'cable modifié , nom:' + nom + '- type_prise :' + type_prise_id + ' - prix:' + prix  + ' - image:' + image_nom + ' - description: ' + description
    flash(message, 'alert-success')
    return redirect('/admin/cable/show')







@admin_cable.route('/admin/cable/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    cable=[]
    commentaires = {}
    return render_template('admin/cable/show_avis.html'
                           , cable=cable
                           , commentaires=commentaires
                           )


@admin_cable.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    cable_id = request.form.get('id_cable', None)
    userId = request.form.get('idUser', None)

    return admin_avis(cable_id)
