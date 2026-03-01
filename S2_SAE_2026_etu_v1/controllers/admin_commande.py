#! /usr/bin/python
# -- coding:utf-8 --

from flask import Blueprint, request, render_template, redirect, session, flash
from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__, template_folder='templates')


@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['GET'])
def admin_commande_show():

    cursor = get_db().cursor()

    sql_commandes = """
        SELECT
            c.id_commande,
            u.login,
            u.id_utilisateur,
            c.date_achat,
            SUM(lc.quantite_commande) AS nbr_articles,
            SUM(lc.quantite_commande * lc.prix) AS prix_total,
            c.etat_id,
            e.libelle
        FROM commande c
        JOIN utilisateur u ON u.id_utilisateur = c.utilisateur_id
        JOIN ligne_commande lc ON lc.commande_id = c.id_commande
        JOIN etat e ON e.id_etat = c.etat_id
        WHERE u.role = 'ROLE_client'
        GROUP BY c.id_commande, u.login, u.id_utilisateur, c.date_achat, c.etat_id, e.libelle
        ORDER BY c.date_achat DESC
    """
    cursor.execute(sql_commandes)
    commandes = cursor.fetchall()
    cables_commande = None
    id_commande = request.args.get('id_commande')

    if id_commande:
        sql_details = """
            SELECT
                c.nom_cable,
                lc.quantite_commande,
                lc.prix,
                (lc.quantite_commande * lc.prix) AS prix_ligne
            FROM ligne_commande lc
            JOIN cable c ON c.id_cable = lc.cable_id
            WHERE lc.commande_id = %s
        """
        cursor.execute(sql_details, (id_commande,))
        cables_commande = cursor.fetchall()

    return render_template(
        'admin/commandes/show.html',
        commandes=commandes,
        cables_commande=cables_commande
    )


@admin_commande.route('/admin/commande/valider', methods=['POST'])
def admin_commande_valider():
    if 'id_user' not in session:
        return redirect('/login')

    cursor = get_db().cursor()
    commande_id = request.form.get('id_commande')

    if commande_id:
        sql_update = """
            UPDATE commande
            SET etat_id = 3
            WHERE id_commande = %s
        """
        cursor.execute(sql_update, (commande_id,))
        get_db().commit()
        flash("Commande expédiée", "success")

    return redirect('/admin/commande/show')
