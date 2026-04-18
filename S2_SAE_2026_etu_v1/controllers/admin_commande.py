#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__, template_folder='templates')


@admin_commande.route('/admin/commande/index')
def admin_commande_index():
    mycursor = get_db().cursor()
    mycursor.execute("""
        SELECT c.id_commande, c.date_achat, c.etat_id, e.libelle,
               u.login, u.nom, u.email,
               SUM(lc.quantite_commande) AS nb_articles,
               SUM(lc.prix * lc.quantite_commande) AS prix_total
        FROM commande c
        JOIN utilisateur u ON c.utilisateur_id=u.id_utilisateur
        JOIN etat e ON c.etat_id=e.id_etat
        LEFT JOIN ligne_commande lc ON lc.commande_id=c.id_commande
        GROUP BY c.id_commande
        ORDER BY c.date_achat DESC
    """)
    commandes = mycursor.fetchall()
    mycursor.execute("SELECT * FROM etat")
    etats = mycursor.fetchall()
    return render_template('admin/commandes/show.html', commandes=commandes, etats=etats)


@admin_commande.route('/admin/commande/show')
def admin_commande_show():
    id_commande = request.args.get('id_commande')
    mycursor = get_db().cursor()
    mycursor.execute("""
        SELECT lc.*, ca.nom_cable, l.nom_longueur, co.nom_couleur
        FROM ligne_commande lc
        JOIN cable ca ON lc.cable_id=ca.id_cable
        LEFT JOIN declinaison_cable dc ON lc.declinaison_cable_id=dc.id_declinaison_cable
        LEFT JOIN longueur l ON dc.longueur_id=l.id_longueur
        LEFT JOIN couleur co ON dc.couleur_id=co.id_couleur
        WHERE lc.commande_id=%s
    """, id_commande)
    lignes = mycursor.fetchall()
    mycursor.execute("""
        SELECT c.*, u.login, u.nom, u.email,
               al.nom AS nom_liv, al.rue AS rue_liv, al.code_postal AS cp_liv, al.ville AS ville_liv,
               af.nom AS nom_fact, af.rue AS rue_fact, af.code_postal AS cp_fact, af.ville AS ville_fact
        FROM commande c
        JOIN utilisateur u ON c.utilisateur_id=u.id_utilisateur
        LEFT JOIN adresse al ON c.adresse_livraison_id=al.id_adresse
        LEFT JOIN adresse af ON c.adresse_facturation_id=af.id_adresse
        WHERE c.id_commande=%s
    """, id_commande)
    commande = mycursor.fetchone()
    mycursor.execute("SELECT * FROM etat")
    etats = mycursor.fetchall()
    return render_template('admin/commandes/show.html',
                           commandes=None, detail_lignes=lignes, commande=commande, etats=etats)


@admin_commande.route('/admin/commande/etat', methods=['POST'])
def admin_commande_etat():
    mycursor = get_db().cursor()
    id_commande = request.form.get('id_commande')
    etat_id = request.form.get('etat_id')
    mycursor.execute("UPDATE commande SET etat_id=%s WHERE id_commande=%s", (etat_id, id_commande))
    get_db().commit()
    flash("État mis à jour", 'alert-success')
    return redirect('/admin/commande/index')
