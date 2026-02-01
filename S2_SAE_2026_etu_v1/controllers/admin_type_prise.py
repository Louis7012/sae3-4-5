#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_type_prise = Blueprint('admin_type_prise', __name__,
                        template_folder='templates')

@admin_type_prise.route('/admin/type-prise/show')
def show_type_prise():
    mycursor = get_db().cursor()
    # sql = '''         '''
    # mycursor.execute(sql)
    # types_prise = mycursor.fetchall()
    types_prise=[]
    return render_template('admin/type_prise/show_type_prise.html', types_prise=types_prise)

@admin_type_prise.route('/admin/type-prise/add', methods=['GET'])
def add_type_prise():
    return render_template('admin/type_prise/add_type_prise.html')

@admin_type_prise.route('/admin/type-prise/add', methods=['POST'])
def valid_add_type_prise():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = '''         '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'type ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/type-prise/show') #url_for('show_type_prise')

@admin_type_prise.route('/admin/type-prise/delete', methods=['GET'])
def delete_type_prise():
    id_type_prise = request.args.get('id_type_prise', '')
    mycursor = get_db().cursor()

    flash(u'suppression type prise , id : ' + id_type_prise, 'alert-success')
    return redirect('/admin/type-prise/show')

@admin_type_prise.route('/admin/type-prise/edit', methods=['GET'])
def edit_type_prise():
    id_type_prise = request.args.get('id_type_prise', '')
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, (id_type_prise,))
    type_prise = mycursor.fetchone()
    return render_template('admin/type_prise/edit_type_prise.html', type_prise=type_prise)

@admin_type_prise.route('/admin/type-prise/edit', methods=['POST'])
def valid_edit_type_prise():
    libelle = request.form['libelle']
    id_type_prise = request.form.get('id_type_prise', '')
    tuple_update = (libelle, id_type_prise)
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    flash(u'type prise modifié, id: ' + id_type_prise + " nom : " + nom_type_prise, 'alert-success')
    return redirect('/admin/type-prise/show')








