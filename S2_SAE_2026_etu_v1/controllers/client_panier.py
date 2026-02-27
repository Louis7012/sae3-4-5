#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                          template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.form.get('id_cable')
    quantite = request.form.get('quantite')


    sql = "SELECT * FROM ligne_panier WHERE cable_id = %s AND utilisateur_id = %s"
    mycursor.execute(sql, (id_cable, id_client))
    cable_panier = mycursor.fetchone()

    if cable_panier is not None and cable_panier['quantite_panier'] >= 1:
        tuple_update = (quantite, id_client, id_cable)
        sql = "UPDATE ligne_panier SET quantite_panier = quantite_panier+%s WHERE utilisateur_id = %s AND cable_id = %s"
        mycursor.execute(sql, tuple_update)
    else:
        tuple_insert = (id_client, id_cable, quantite)
        sql = """INSERT INTO ligne_panier(utilisateur_id, cable_id, quantite_panier, date_ajout)
                 VALUES (%s, %s, %s, current_timestamp)"""
        mycursor.execute(sql, tuple_insert)

    sql="UPDATE cable SET stock=stock-%s WHERE id_cable=%s"
    mycursor.execute(sql, (quantite, id_cable))

    get_db().commit()
    return redirect('/client/cable/show')

    #id_declinaison_cable=request.form.get('id_declinaison_cable',None)
    id_declinaison_cable = 1

    # ajout dans le panier d'une déclinaison d'un cable (si 1 declinaison : immédiat sinon => vu pour faire un choix
    # sql = '''    '''
    # mycursor.execute(sql, (id_cable))
    # declinaisons = mycursor.fetchall()
    # if len(declinaisons) == 1:
    #     id_declinaison_cable = declinaisons[0]['id_declinaison_cable']
    # elif len(declinaisons) == 0:
    #     abort("pb nb de declinaison")
    # else:
    #     sql = '''   '''
    #     mycursor.execute(sql, (id_cable))
    #     cable = mycursor.fetchone()
    #     return render_template('client/boutique/declinaison_cable.html'
    #                                , declinaisons=declinaisons
    #                                , quantite=quantite
    #                                , cable=cable)

    # ajout dans le panier d'un cable


    return redirect('/client/cable/show')

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_cable = request.form.get('id_cable','')
    quantite = 1

    # ---------
    # partie 2 : on supprime une déclinaison de l'cable
    # id_declinaison_cable = request.form.get('id_declinaison_cable', None)

    sql = ''' SELECT quantite_panier
        FROM ligne_panier
        WHERE utilisateur_id = %s AND cable_id = %s'''
    mycursor.execute(sql, (id_client, id_cable))
    cable_panier = mycursor.fetchone()

    if not(cable_panier is None) and cable_panier['quantite'] > 1:
        sql = ''' UPDATE ligne_panier
                SET quantite_panier = quantite_panier - 1
                WHERE utilisateur_id = %s AND cable_id = %s '''
        mycursor.execute(sql, (id_client, id_cable))
    else:
        sql = ''' DELETE FROM ligne_panier
                WHERE utilisateur_id = %s AND cable_id = %s'''
        mycursor.execute(sql, (id_client, id_cable))

    # mise à jour du stock de l'article disponible
    get_db().commit()
    return redirect('/client/cable/show')





@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']
    quantite = request.form.get('quantite')
    id_cable = request.form.get('id_cable')
    sql = ''' SELECT cable_id, quantite_panier
        FROM ligne_panier
        WHERE utilisateur_id = %s
        '''
    mycursor.execute(sql, (client_id,))
    items_panier = []
    for item in items_panier:
        sql = ''' DELETE FROM ligne_panier
        WHERE utilisateur_id = %s'''
        mycursor.execute(sql, (client_id,))

        sql2=''' UPDATE cable
            SET stock = stock + %s
            WHERE id_cable = %s'''
        mycursor.execute(sql2, (quantite, id_cable))
        get_db().commit()
    return redirect('/client/cable/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    #id_declinaison_cable = request.form.get('id_declinaison_cable')
    id_cable = request.form.get('id_cable')
    quantite = request.form.get('quantite')


    sql = '''SELECT *
    FROM ligne_panier
    WHERE cable_id = %s AND utilisateur_id = %s;'''
    mycursor.execute(sql, (id_cable, id_client))


    sql = '''DELETE FROM ligne_panier
            WHERE utilisateur_id = %s AND cable_id = %s'''

    mycursor.execute(sql, (id_client, id_cable))

    sql2='''UPDATE cable
            SET stock = stock + %s
            WHERE id_cable = %s'''
    mycursor.execute(sql, (quantite, id_cable))
    get_db().commit()
    return redirect('/client/cable/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types', None)
    # test des variables puis
    # mise en session des variables
    return redirect('/client/cable/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    # suppression  des variables en session
    print("suppr filtre")
    return redirect('/client/cable/show')