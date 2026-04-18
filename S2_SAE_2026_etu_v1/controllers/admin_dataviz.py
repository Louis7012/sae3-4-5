#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template
from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__, template_folder='templates')


def calculer_pourcentages(liste, cle):
    """Calcule le pourcentage par rapport au maximum pour les barres CSS."""
    max_val = 0
    for item in liste:
        if item[cle] and item[cle] > max_val:
            max_val = item[cle]
    if max_val == 0:
        max_val = 1
    for item in liste:
        if item[cle]:
            item['pct_' + cle] = int(item[cle] / max_val * 100)
        else:
            item['pct_' + cle] = 0
    return liste


@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_cable_stock():
    mycursor = get_db().cursor()

    mycursor.execute("""
        SELECT co.nom_couleur AS libelle,
               SUM(dc.stock) AS nbr_cables,
               SUM(dc.stock * dc.prix) AS cout_stock
        FROM declinaison_cable dc
        JOIN couleur co ON dc.couleur_id = co.id_couleur
        GROUP BY co.id_couleur
        ORDER BY cout_stock DESC
    """)
    datas_show = mycursor.fetchall()
    datas_show = calculer_pourcentages(datas_show, 'nbr_cables')

    mycursor.execute("""
        SELECT tp.nom_type_prise AS libelle, SUM(c.stock) AS stock_total
        FROM cable c
        JOIN type_prise tp ON c.type_prise_id = tp.id_type_prise
        GROUP BY tp.id_type_prise
        ORDER BY stock_total DESC
    """)
    stock_par_type = mycursor.fetchall()
    stock_par_type = calculer_pourcentages(stock_par_type, 'stock_total')

    return render_template('admin/dataviz/dataviz_etat_1.html',
                           datas_show=datas_show, stock_par_type=stock_par_type)


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()
    mycursor.execute("""
        SELECT LEFT(a.code_postal, 2) AS dep,
               COUNT(DISTINCT c.id_commande) AS nombre,
               SUM(lc.prix * lc.quantite_commande) AS chiffre_affaires
        FROM commande c
        JOIN adresse a ON c.adresse_livraison_id = a.id_adresse
        LEFT JOIN ligne_commande lc ON lc.commande_id = c.id_commande
        GROUP BY dep
        ORDER BY nombre DESC
    """)
    adresses = mycursor.fetchall()
    adresses = calculer_pourcentages(adresses, 'nombre')
    return render_template('admin/dataviz/dataviz_etat_map.html', adresses=adresses)


@admin_dataviz.route('/admin/dataviz/commentaires')
def show_dataviz_commentaires():
    mycursor = get_db().cursor()
    mycursor.execute("""
        SELECT tp.nom_type_prise AS categorie,
               COUNT(DISTINCT a.id_avis) AS nb_notes,
               AVG(a.note) AS note_moyenne,
               COUNT(DISTINCT com.id_commentaire) AS nb_commentaires
        FROM type_prise tp
        LEFT JOIN cable c ON c.type_prise_id = tp.id_type_prise
        LEFT JOIN avis a ON a.cable_id = c.id_cable
        LEFT JOIN commentaire com ON com.cable_id = c.id_cable
            AND com.commentaire_parent_id IS NULL
        GROUP BY tp.id_type_prise
    """)
    stats_categories = mycursor.fetchall()
    # Arrondir la note moyenne en Python
    for s in stats_categories:
        if s['note_moyenne']:
            s['note_moyenne'] = round(float(s['note_moyenne']), 1)
    stats_categories = calculer_pourcentages(stats_categories, 'nb_commentaires')

    categorie_sel = request.args.get('categorie', None)
    stats_articles = None
    if categorie_sel:
        mycursor.execute("""
            SELECT c.nom_cable, c.id_cable,
                   COUNT(DISTINCT a.id_avis) AS nb_notes,
                   AVG(a.note) AS note_moyenne,
                   COUNT(DISTINCT com.id_commentaire) AS nb_commentaires
            FROM cable c
            JOIN type_prise tp ON c.type_prise_id = tp.id_type_prise
            LEFT JOIN avis a ON a.cable_id = c.id_cable
            LEFT JOIN commentaire com ON com.cable_id = c.id_cable
                AND com.commentaire_parent_id IS NULL
            WHERE tp.nom_type_prise = %s
            GROUP BY c.id_cable
        """, categorie_sel)
        stats_articles = mycursor.fetchall()
        for s in stats_articles:
            if s['note_moyenne']:
                s['note_moyenne'] = round(float(s['note_moyenne']), 1)
        stats_articles = calculer_pourcentages(stats_articles, 'nb_notes')

    mycursor.execute("SELECT nom_type_prise FROM type_prise")
    categories = [r['nom_type_prise'] for r in mycursor.fetchall()]

    return render_template('admin/dataviz/dataviz_commentaires.html',
                           stats_categories=stats_categories,
                           stats_articles=stats_articles,
                           categorie_sel=categorie_sel,
                           categories=categories)


@admin_dataviz.route('/admin/dataviz/wishlist')
def show_dataviz_wishlist():
    mycursor = get_db().cursor()
    mycursor.execute("""
        SELECT tp.nom_type_prise AS categorie,
               COUNT(DISTINCT le.utilisateur_id) AS nb_wishlist,
               COUNT(DISTINCT h.id_historique) AS nb_historique_mois
        FROM type_prise tp
        LEFT JOIN cable c ON c.type_prise_id = tp.id_type_prise
        LEFT JOIN liste_envies le ON le.cable_id = c.id_cable
        LEFT JOIN historique h ON h.cable_id = c.id_cable
        GROUP BY tp.id_type_prise
    """)
    stats = mycursor.fetchall()
    stats = calculer_pourcentages(stats, 'nb_wishlist')
    stats = calculer_pourcentages(stats, 'nb_historique_mois')
    return render_template('admin/dataviz/dataviz_wishlist.html', stats=stats)
