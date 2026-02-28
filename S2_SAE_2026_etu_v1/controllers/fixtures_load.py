#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                        template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()
    sql='''DROP TABLE IF EXISTS ligne_panier;
    DROP TABLE IF EXISTS ligne_commande;
    DROP TABLE IF EXISTS commande;
    DROP TABLE IF EXISTS etat;
    DROP TABLE IF EXISTS cable;
    DROP TABLE IF EXISTS type_prise;
    DROP TABLE IF EXISTS longueur;
    DROP TABLE IF EXISTS utilisateur;
    '''

    mycursor.execute(sql)
    sql = '''
    CREATE TABLE utilisateur(
       id_utilisateur INT AUTO_INCREMENT,
       login VARCHAR(255),
       email VARCHAR(255),
       nom VARCHAR(50),
       password VARCHAR(255),
       role VARCHAR(255),
       PRIMARY KEY(id_utilisateur)
    ) DEFAULT CHARSET=utf8;  
    '''
    mycursor.execute(sql)
    sql=''' 
    CREATE TABLE utilisateur(
       id_utilisateur INT AUTO_INCREMENT,
       login VARCHAR(255),
       email VARCHAR(255),
       nom VARCHAR(50),
       password VARCHAR(255),
       role VARCHAR(255),
       PRIMARY KEY(id_utilisateur)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)

    sql=''' 
    CREATE TABLE type_prise(
       id_type_prise INT AUTO_INCREMENT,
       nom_type_prise VARCHAR(50),
       PRIMARY KEY(id_type_prise)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)
    sql=''' 
INSERT INTO type_prise
    '''
    mycursor.execute(sql)


    sql=''' 
    CREATE TABLE etat (
   id_etat INT AUTO_INCREMENT,
   libelle VARCHAR(255),
   PRIMARY KEY(id_etat)
) DEFAULT CHARSET=utf8;  
    '''
    mycursor.execute(sql)
    sql = ''' 
INSERT INTO etat (id_etat, libelle) VALUES
(1, 'en attente'),
(2, 'payée'),
(3, 'expédiée'),
(4, 'livrée'),
(5, 'annulée');
     '''
    mycursor.execute(sql)

    sql = ''' 
CREATE TABLE cable (
   id_cable INT AUTO_INCREMENT,
   nom_cable VARCHAR(50),
   couleur VARCHAR(50),
   prix_cable DECIMAL(15,2),
   blindage VARCHAR(50),
   fournisseur VARCHAR(50),
   marque VARCHAR(50),
   photo VARCHAR(50),
   stock INT,
   type_prise_id INT NOT NULL,
   longueur_id INT NOT NULL,
   PRIMARY KEY(id_cable),
   FOREIGN KEY(type_prise_id) REFERENCES type_prise(id_type_prise),
   FOREIGN KEY(longueur_id) REFERENCES longueur(id_longueur)
) DEFAULT CHARSET=utf8;  
     '''
    mycursor.execute(sql)
    sql = ''' 
    INSERT INTO cable
    (nom_cable, couleur, prix_cable, blindage, fournisseur, marque, photo, stock, type_prise_id, longueur_id)
    VALUES
    ('HDMI Basic 1m', 'Noir', 9.99, 'Oui', 'TechSupply', 'Generic', 'HDMI_1.png', 50, 1, 2),
    ('HDMI Premium 2m', 'Noir', 14.99, 'Oui', 'TechSupply', 'Belkin', 'HDMI_3.png', 40, 1, 3),
    ('HDMI Gold 3m', 'Noir', 19.99, 'Oui', 'CablePro', 'UGreen', 'HDMI_4.png', 30, 1, 4),
    ('HDMI Slim 5m', 'Noir', 12.99, 'Non', 'CablePro', 'Anker', 'HDMI_2.png', 35, 1, 5),
    ('HDMI Ultra 0.5m', 'Noir', 7.99, 'Oui', 'TechSupply', 'Generic', 'HDMI_5.png', 60, 1, 1);
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE commande (
       id_commande INT AUTO_INCREMENT,
       date_achat DATE,
       etat_id INT NOT NULL,
       utilisateur_id INT NOT NULL,
       PRIMARY KEY(id_commande),
       FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
       FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
    ) DEFAULT CHARSET=utf8;  
    '''
    mycursor.execute(sql)
    sql = ''' 
    INSERT INTO commande (id_commande, date_achat, etat_id, utilisateur_id) VALUES
    (1001, '2026-01-10', 4, 1),
    (1002, '2026-01-15', 2, 1),
    (1003, '2026-01-20', 1, 2);
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE ligne_commande(
       cable_id INT,
       commande_id INT,
       quantite_commande INT,
       prix DECIMAL(15,2),
       PRIMARY KEY(cable_id, commande_id),
       FOREIGN KEY(cable_id) REFERENCES cable(id_cable),
       FOREIGN KEY(commande_id) REFERENCES commande(id_commande)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)
    sql = ''' 
    INSERT INTO ligne_commande (cable_id, commande_id, quantite_commande, prix) VALUES
    (1, 1001, 2, 990),
    (3, 1002, 1, 1990),
    (2, 1002, 2, 1490),
    (4, 1003, 3, 650);
    '''
    mycursor.execute(sql)



    sql = ''' 
CREATE TABLE ligne_panier (
   cable_id INT,
   utilisateur_id INT,
   quantite_panier INT,
   date_ajout DATE,
   PRIMARY KEY(cable_id, utilisateur_id),
   FOREIGN KEY(cable_id) REFERENCES cable(id_cable),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
) DEFAULT CHARSET=utf8;  
'''
    mycursor.execute(sql)


    get_db().commit()
    return redirect('/')
