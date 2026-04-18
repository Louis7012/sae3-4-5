#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, redirect
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__, template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()
    drops = [
        "DROP TABLE IF EXISTS historique",
        "DROP TABLE IF EXISTS liste_envies",
        "DROP TABLE IF EXISTS avis",
        "DROP TABLE IF EXISTS commentaire",
        "DROP TABLE IF EXISTS ligne_panier",
        "DROP TABLE IF EXISTS ligne_commande",
        "DROP TABLE IF EXISTS commande",
        "DROP TABLE IF EXISTS declinaison_cable",
        "DROP TABLE IF EXISTS cable",
        "DROP TABLE IF EXISTS etat",
        "DROP TABLE IF EXISTS adresse",
        "DROP TABLE IF EXISTS longueur",
        "DROP TABLE IF EXISTS couleur",
        "DROP TABLE IF EXISTS type_prise",
        "DROP TABLE IF EXISTS utilisateur",
    ]
    for sql in drops:
        mycursor.execute(sql)

    creates = [
        """CREATE TABLE type_prise(id_type_prise INT AUTO_INCREMENT, nom_type_prise VARCHAR(50), PRIMARY KEY(id_type_prise))""",
        """CREATE TABLE longueur(id_longueur INT AUTO_INCREMENT, nom_longueur VARCHAR(50), PRIMARY KEY(id_longueur))""",
        """CREATE TABLE couleur(id_couleur INT AUTO_INCREMENT, nom_couleur VARCHAR(50), code_hex VARCHAR(10), PRIMARY KEY(id_couleur))""",
        """CREATE TABLE utilisateur(id_utilisateur INT AUTO_INCREMENT, login VARCHAR(255), email VARCHAR(255), nom VARCHAR(50), password VARCHAR(255), role VARCHAR(255), PRIMARY KEY(id_utilisateur))""",
        """CREATE TABLE adresse(id_adresse INT AUTO_INCREMENT, utilisateur_id INT NOT NULL, nom VARCHAR(100), rue VARCHAR(255), code_postal VARCHAR(10), ville VARCHAR(100), est_favorite TINYINT(1), est_valide TINYINT(1) DEFAULT 1, PRIMARY KEY(id_adresse), FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur))""",
        """CREATE TABLE etat(id_etat INT AUTO_INCREMENT, libelle VARCHAR(255), PRIMARY KEY(id_etat))""",
        """CREATE TABLE cable(id_cable INT AUTO_INCREMENT, nom_cable VARCHAR(50), couleur VARCHAR(50), prix_cable DECIMAL(15,2), blindage VARCHAR(50), fournisseur VARCHAR(50), marque VARCHAR(50), photo VARCHAR(50), stock INT, type_prise_id INT NOT NULL, longueur_id INT NOT NULL, PRIMARY KEY(id_cable), FOREIGN KEY(type_prise_id) REFERENCES type_prise(id_type_prise), FOREIGN KEY(longueur_id) REFERENCES longueur(id_longueur))""",
        """CREATE TABLE declinaison_cable(id_declinaison_cable INT AUTO_INCREMENT, cable_id INT NOT NULL, longueur_id INT NOT NULL, couleur_id INT NOT NULL, stock INT, prix DECIMAL(15,2), PRIMARY KEY(id_declinaison_cable), FOREIGN KEY(cable_id) REFERENCES cable(id_cable), FOREIGN KEY(longueur_id) REFERENCES longueur(id_longueur), FOREIGN KEY(couleur_id) REFERENCES couleur(id_couleur))""",
        """CREATE TABLE commande(id_commande INT AUTO_INCREMENT, date_achat DATE, etat_id INT NOT NULL, utilisateur_id INT NOT NULL, adresse_livraison_id INT, adresse_facturation_id INT, PRIMARY KEY(id_commande), FOREIGN KEY(etat_id) REFERENCES etat(id_etat), FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur), FOREIGN KEY(adresse_livraison_id) REFERENCES adresse(id_adresse), FOREIGN KEY(adresse_facturation_id) REFERENCES adresse(id_adresse))""",
        """CREATE TABLE ligne_commande(id_ligne_commande INT AUTO_INCREMENT, cable_id INT, commande_id INT, declinaison_cable_id INT, quantite_commande INT, prix DECIMAL(15,2), PRIMARY KEY(id_ligne_commande), FOREIGN KEY(cable_id) REFERENCES cable(id_cable), FOREIGN KEY(commande_id) REFERENCES commande(id_commande))""",
        """CREATE TABLE ligne_panier(id_panier INT AUTO_INCREMENT, cable_id INT, utilisateur_id INT, declinaison_cable_id INT, quantite_panier INT, date_ajout DATETIME, PRIMARY KEY(id_panier), FOREIGN KEY(cable_id) REFERENCES cable(id_cable), FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur))""",
        """CREATE TABLE commentaire(id_commentaire INT AUTO_INCREMENT, utilisateur_id INT NOT NULL, cable_id INT NOT NULL, commentaire TEXT, date_publication DATETIME, valider TINYINT(1), commentaire_parent_id INT, PRIMARY KEY(id_commentaire), FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur), FOREIGN KEY(cable_id) REFERENCES cable(id_cable))""",
        """CREATE TABLE avis(id_avis INT AUTO_INCREMENT, utilisateur_id INT NOT NULL, cable_id INT NOT NULL, note DECIMAL(3,1), PRIMARY KEY(id_avis), UNIQUE KEY(utilisateur_id, cable_id), FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur), FOREIGN KEY(cable_id) REFERENCES cable(id_cable))""",
        """CREATE TABLE liste_envies(utilisateur_id INT, cable_id INT, date_ajout DATETIME, rang INT, PRIMARY KEY(utilisateur_id, cable_id), FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur), FOREIGN KEY(cable_id) REFERENCES cable(id_cable))""",
        """CREATE TABLE historique(id_historique INT AUTO_INCREMENT, utilisateur_id INT NOT NULL, cable_id INT NOT NULL, date_consultation DATETIME, nb_consultations INT DEFAULT 1, PRIMARY KEY(id_historique), UNIQUE KEY(utilisateur_id, cable_id), FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur), FOREIGN KEY(cable_id) REFERENCES cable(id_cable))""",
    ]
    for sql in creates:
        mycursor.execute(sql)

    inserts = [
        "INSERT INTO type_prise (nom_type_prise) VALUES ('HDMI'),('Jack'),('RJ45'),('USB-C')",
        "INSERT INTO longueur (nom_longueur) VALUES ('0.5 m'),('1 m'),('2 m'),('3 m'),('5 m')",
        "INSERT INTO couleur (nom_couleur, code_hex) VALUES ('Unique','#888888'),('Noir','#000000'),('Blanc','#FFFFFF'),('Gris','#808080'),('Rouge','#FF0000'),('Bleu','#0000FF')",
        "INSERT INTO etat (id_etat, libelle) VALUES (1,'en attente'),(2,'payée'),(3,'expédiée'),(4,'livrée'),(5,'annulée')",
        """INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom) VALUES
(1,'admin','admin@admin.fr','pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988','ROLE_admin','admin'),
(2,'client','client@client.fr','pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349','ROLE_client','client'),
(3,'client2','client2@client2.fr','pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080','ROLE_client','client2')""",
        """INSERT INTO adresse (utilisateur_id, nom, rue, code_postal, ville, est_favorite, est_valide) VALUES
(2,'client Maison','12 rue de la Paix','75001','Paris',1,1),
(2,'client Bureau','5 avenue des Champs','75008','Paris',0,1),
(3,'client2 Home','3 rue du Port','25000','Besançon',1,1)""",
        """INSERT INTO cable (nom_cable, couleur, prix_cable, blindage, fournisseur, marque, photo, stock, type_prise_id, longueur_id) VALUES
('HDMI Basic 1m','Noir',9.99,'Oui','TechSupply','Generic','HDMI_1.png',50,1,2),
('HDMI Premium 2m','Noir',14.99,'Oui','TechSupply','Belkin','HDMI_3.png',40,1,3),
('HDMI Gold 3m','Noir',19.99,'Oui','CablePro','UGreen','HDMI_4.png',30,1,4),
('HDMI Slim 5m','Noir',12.99,'Non','CablePro','Anker','HDMI_2.png',35,1,5),
('HDMI Ultra 0.5m','Noir',7.99,'Oui','TechSupply','Generic','HDMI_5.png',60,1,1),
('Jack Audio 1m','Noir',5.99,'Non','AudioPlus','Sony','jack_1.png',80,2,2),
('Jack Stéréo 1m','Noir',7.49,'Oui','AudioPlus','JBL','jack_2.png',70,2,2),
('Jack Pro 2m','Noir',9.99,'Oui','SoundTech','Bose','jack_4.png',50,2,3),
('Jack Compact 0.5m','Noir',4.99,'Non','SoundTech','Generic','jack_3.png',90,2,1),
('Jack Long 3m','Noir',11.99,'Oui','AudioPlus','Sennheiser','jack_5.png',40,2,4),
('RJ45 Cat6 1m','Noir',6.99,'Oui','NetCorp','TP-Link','RJ45_1.png',100,3,2),
('RJ45 Cat6 2m','Blanc',9.49,'Oui','NetCorp','D-Link','RJ45_2.png',80,3,3),
('RJ45 Cat7 3m','Noir',14.99,'Oui','CablePro','UGreen','RJ45_3.png',60,3,4),
('RJ45 Cat5e 5m','Noir',7.99,'Non','NetCorp','Generic','RJ45_4.png',90,3,5),
('RJ45 Court 0.5m','Blanc',4.49,'Non','CablePro','Generic','RJ45_5.png',120,3,1),
('USB-C Charge 1m','Gris',8.99,'Oui','MobileTech','Samsung','USBc_1.png',70,4,2),
('USB-C Data 3m','Noir',10.99,'Oui','MobileTech','Anker','USBc_2.png',65,4,4),
('USB-C Fast 2m','Noir',13.99,'Oui','CablePro','UGreen','USBc_3.png',50,4,3),
('USB-C Court 0.5m','Gris',6.49,'Non','MobileTech','Generic','USBc_4.png',85,4,1),
('USB-C Long 3m','Noir',16.99,'Oui','CablePro','Belkin','USBc_5.png',40,4,4)""",
        """INSERT INTO declinaison_cable (cable_id, longueur_id, couleur_id, stock, prix) VALUES
(1,2,2,20,9.99),(1,2,3,15,9.99),(1,2,4,10,9.99),
(2,3,2,20,14.99),(2,3,6,10,14.99),
(3,4,2,15,19.99),(3,4,5,8,21.99),
(6,2,1,50,5.99),
(11,2,2,40,6.99),(11,2,3,30,6.99),
(16,2,2,35,8.99),(16,2,4,25,8.99),(16,2,6,15,9.99)""",
        # stock mis à jour en Python après insertion (voir ci-dessous)
        "SELECT 1",  # requête neutre (le stock est mis à jour ensuite)
        """INSERT INTO commande (id_commande, date_achat, etat_id, utilisateur_id, adresse_livraison_id, adresse_facturation_id) VALUES
(1001,'2026-01-10',4,2,1,1),(1002,'2026-01-15',2,2,2,1),(1003,'2026-01-20',1,3,3,3)""",
        """INSERT INTO ligne_commande (cable_id, commande_id, declinaison_cable_id, quantite_commande, prix) VALUES
(1,1001,1,2,9.99),(3,1002,7,1,19.99),(2,1002,4,2,14.99),(6,1003,8,3,5.99)""",
        """INSERT INTO commentaire (utilisateur_id, cable_id, commentaire, date_publication, valider) VALUES
(2,1,'Très bon câble HDMI, image parfaite !','2026-01-11 10:00:00',1),
(2,1,'La couleur blanc est magnifique','2026-01-12 14:00:00',0),
(3,1,'Rapport qualité/prix excellent','2026-01-13 09:00:00',0),
(2,11,'Super câble réseau, rapide','2026-01-16 11:00:00',1)""",
        """INSERT INTO avis (utilisateur_id, cable_id, note) VALUES (2,1,4.5),(3,1,4.0),(2,11,5.0)""",
        """INSERT INTO liste_envies (utilisateur_id, cable_id, date_ajout, rang) VALUES
(2,2,'2026-01-20 10:00:00',1),(2,5,'2026-01-21 10:00:00',2),(2,7,'2026-01-22 10:00:00',3),
(3,1,'2026-01-20 09:00:00',1),(3,4,'2026-01-23 10:00:00',2)""",
        """INSERT INTO historique (utilisateur_id, cable_id, date_consultation, nb_consultations) VALUES
(2,1,'2026-02-01 10:00:00',3),(2,2,'2026-02-02 11:00:00',1),(2,3,'2026-02-03 09:00:00',2),
(3,1,'2026-02-01 15:00:00',1),(3,5,'2026-02-04 10:00:00',2)""",
    ]
    for sql in inserts:
        mycursor.execute(sql)

    # Mettre à jour le stock de chaque câble qui a des déclinaisons
    cables_avec_decl = [1, 2, 3, 6, 11, 16]
    for id_cable in cables_avec_decl:
        mycursor.execute("SELECT SUM(stock) AS total FROM declinaison_cable WHERE cable_id=%s", id_cable)
        row = mycursor.fetchone()
        nouveau_stock = row['total'] if row['total'] else 0
        mycursor.execute("UPDATE cable SET stock=%s WHERE id_cable=%s", (nouveau_stock, id_cable))

    get_db().commit()
    return redirect('/')
