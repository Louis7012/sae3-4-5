-- use S2_BDD;
DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS cable;
DROP TABLE IF EXISTS type_prise;
DROP TABLE IF EXISTS longueur;
DROP TABLE IF EXISTS utilisateur;

CREATE TABLE type_prise(
   id_type_prise INT AUTO_INCREMENT,
   nom_type_prise VARCHAR(50),
   PRIMARY KEY(id_type_prise)
);

CREATE TABLE longueur(
   id_longueur INT AUTO_INCREMENT,
   nom_longueur VARCHAR(50),
   PRIMARY KEY(id_longueur)
);

CREATE TABLE utilisateur(
   id_utilisateur INT AUTO_INCREMENT,
   login VARCHAR(255),
   email VARCHAR(255),
   nom VARCHAR(50),
   password VARCHAR(255),
   role VARCHAR(255),
   PRIMARY KEY(id_utilisateur)
);

CREATE TABLE etat(
   id_etat INT AUTO_INCREMENT,
   libelle VARCHAR(255),
   PRIMARY KEY(id_etat)
);

CREATE TABLE cable(
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
);

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat DATE,
   etat_id INT NOT NULL,
   utilisateur_id INT NOT NULL,
   PRIMARY KEY(id_commande),
   FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE ligne_commande(
   cable_id INT,
   commande_id INT,
   quantite_commande INT,
   prix DECIMAL(15,2),
   PRIMARY KEY(cable_id, commande_id),
   FOREIGN KEY(cable_id) REFERENCES cable(id_cable),
   FOREIGN KEY(commande_id) REFERENCES commande(id_commande)
);

CREATE TABLE ligne_panier(
   cable_id INT,
   utilisateur_id INT,
   quantite_panier INT,
   date_ajout DATE,
   PRIMARY KEY(cable_id, utilisateur_id),
   FOREIGN KEY(cable_id) REFERENCES cable(id_cable),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
);


-- =========================
-- 1) TABLES DE REFERENCE
-- =========================

INSERT INTO type_prise (nom_type_prise) VALUES
('HDMI'),
('Jack'),
('RJ45'),
('USB-C');

INSERT INTO longueur (nom_longueur) VALUES
('0.5 m'),
('1 m'),
('2 m'),
('3 m'),
('5 m');

INSERT INTO etat (id_etat, libelle) VALUES
(1, 'en attente'),
(2, 'payée'),
(3, 'expédiée'),
(4, 'livrée'),
(5, 'annulée');

-- =========================
-- 2) UTILISATEURS
-- =========================

    INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom) VALUES
(1,'admin','admin@admin.fr',
    'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
    'ROLE_admin','admin'),
(2,'client','client@client.fr',
    'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
    'ROLE_client','client'),
(3,'client2','client2@client2.fr',
    'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
    'ROLE_client','client2');

-- =========================
-- 3) CABLES
--   #Id_type_prise et #Id_longueur
--   (ici on suppose que les insert précédents ont créé:
--    type_prise: 1..5 et longueur: 1..5)
-- =========================

INSERT INTO cable
(nom_cable, couleur, prix_cable, blindage, fournisseur, marque, photo, stock, type_prise_id, longueur_id)
VALUES
('HDMI Basic 1m', 'Noir', 9.99, 'Oui', 'TechSupply', 'Generic', 'HDMI_1.png', 50, 1, 2),
('HDMI Premium 2m', 'Noir', 14.99, 'Oui', 'TechSupply', 'Belkin', 'HDMI_3.png', 40, 1, 3),
('HDMI Gold 3m', 'Noir', 19.99, 'Oui', 'CablePro', 'UGreen', 'HDMI_4.png', 30, 1, 4),
('HDMI Slim 5m', 'Noir', 12.99, 'Non', 'CablePro', 'Anker', 'HDMI_2.png', 35, 1, 5),
('HDMI Ultra 0.5m', 'Noir', 7.99, 'Oui', 'TechSupply', 'Generic', 'HDMI_5.png', 60, 1, 1),

('Jack Audio 1m', 'Noir', 5.99, 'Non', 'AudioPlus', 'Sony', 'jack_1.png', 80, 2, 2),
('Jack Stéréo 1m', 'Noir', 7.49, 'Oui', 'AudioPlus', 'JBL', 'jack_2.png', 70, 2, 2),
('Jack Pro 2m', 'Noir', 9.99, 'Oui', 'SoundTech', 'Bose', 'jack_4.png', 50, 2, 3),
('Jack Compact 0.5m', 'Noir', 4.99, 'Non', 'SoundTech', 'Generic', 'jack_3.png', 90, 2, 1),
('Jack Long 3m', 'Noir', 11.99, 'Oui', 'AudioPlus', 'Sennheiser', 'jack_5.png', 40, 2, 4),

('RJ45 Cat6 1m', 'Noir', 6.99, 'Oui', 'NetCorp', 'TP-Link', 'RJ45_1.png', 100, 3, 2),
('RJ45 Cat6 2m', 'Blanc', 9.49, 'Oui', 'NetCorp', 'D-Link', 'RJ45_2.png', 80, 3, 3),
('RJ45 Cat7 3m', 'Noir', 14.99, 'Oui', 'CablePro', 'UGreen', 'RJ45_3.png', 60, 3, 4),
('RJ45 Cat5e 5m', 'Noir', 7.99, 'Non', 'NetCorp', 'Generic', 'RJ45_4.png', 90, 3, 5),
('RJ45 Court 0.5m', 'Blanc', 4.49, 'Non', 'CablePro', 'Generic', 'RJ45_5.png', 120, 3, 1),

('USB-C Charge 1m', 'Gris', 8.99, 'Oui', 'MobileTech', 'Samsung', 'USBc_1.png', 70, 4, 2),
('USB-C Data 3m', 'Noir', 10.99, 'Oui', 'MobileTech', 'Anker', 'USBc_2.png', 65, 4, 4),
('USB-C Fast 2m', 'Noir', 13.99, 'Oui', 'CablePro', 'UGreen', 'USBc_3.png', 50, 4, 3),
('USB-C Court 0.5m', 'Gris', 6.49, 'Non', 'MobileTech', 'Generic', 'USBc_4.png', 85, 4, 1),
('USB-C Long 3m', 'Noir', 16.99, 'Oui', 'CablePro', 'Belkin', 'USBc_5.png', 40, 4, 4);


-- =========================
-- 4) COMMANDES
-- =========================

INSERT INTO commande (id_commande, date_achat, etat_id, utilisateur_id) VALUES
(1001, '2026-01-10', 4, 1),
(1002, '2026-01-15', 2, 1),
(1003, '2026-01-20', 1, 2);
-- =========================
-- 5) LIGNES DE COMMANDE
-- =========================

INSERT INTO ligne_commande (cable_id, commande_id, quantite_commande, prix) VALUES
(1, 1001, 2, 9.90),
(3, 1002, 1, 19.90),
(2, 1002, 2, 14.90),
(4, 1003, 3, 6.50);

-- =========================
-- 6) PANIER
-- =========================

INSERT INTO ligne_panier (cable_id, utilisateur_id, quantite_panier, date_ajout) VALUES
(2, 1, 1, '2026-01-29'),
(1, 2, 1, '2026-01-27'),
(3, 2, 1, '2026-01-29');




