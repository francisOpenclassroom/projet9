# -*- coding: utf-8 -*-

# TODO : ne pas oublier de copier les fichiers des configs pour la restauration !
# TODO : Supprimer le fichier quotidienne apres un cycle d'une semaine
# TODO : Coriger la copie SFTP des données (le dossier source et base est incorrect

import locale
import datetime
import sys
import os
import shutil
from itertools import islice
import pysftp
import paramiko

if sys.platform.startswith("darwin"):

    locale.setlocale(locale.LC_ALL, 'fr_FR')
else:
    locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')


class GestionFichier:
    def __init__(self):

        # Déclaration des variables
        self.nom_de_fichier = ""
        self.jour = datetime.datetime.now()
        self.jour_de_lannee = datetime.datetime.now().timetuple().tm_yday
        self.jour_semaine = self.jour.strftime("%A")
        self.format_date = str(self.jour.replace(microsecond=0)).replace(" ", "_").replace(":", "_").replace("-", "_")
        annee, numero_semaine, numero_jour_semaine = self.jour.isocalendar()
        self.numero_semaine = numero_semaine
        self.numero_jour_semaine = numero_jour_semaine
        self.type = "C"
        self.indice = 0
        self.indice_jour = 0
        self.exec_jour = 1
        self.masque = ""
        self.path_du_jour = ""
        self.message_log = ""
        self.dossier_backup = "backup"
        self.dossier_config = "config"
        self.path_dossier_config = ""
        self.dossier_annee = str(annee)
        self.fichier_snar = "backup.snar"
        self.dossier_source = "/var/www/html/www.projet9-wordpress.com " \
                              "/etc/apache2/sites-available/www.projet9-wordpress.com.conf " \
                              "/etc/apache2/sites-enabled/www.projet9-wordpress.com.conf"
        self.remote_base = "/var/rotation_backup/backup/"
        self.mariabd_full_path = ""
        self.nom_dir_mariabd = ""
        self.path_hebdomadaire = ""
        self.dic_rotation = {}
        self.dic_users = {}
        self.path_local = os.getcwd()
        self.db_user = ""
        self.db_passwd = ""
        self.login_user = ""
        self.login_passwd = ""
        self.host_address = ""
        self.host_port = 22

        # Exécution des fonctions de base
        self.creation_dossier_config()
        self.fichier_users()
        self.config_ini()
        self.derniere_execution()
        self.copy_pysftp()

# Creation des dossiers de configuration
    def creation_dossier_config(self):
        self.path_dossier_config = self.dossier_backup + "/" + self.dossier_config + "/"
        if not os.path.isdir(self.path_dossier_config):
            os.makedirs(self.path_dossier_config)

    def fichier_users(self):
        if not os.path.isfile("users.ini"):
            contenu = "Login_user=\nLogin_passwd=\nDB_user=\nDB_passwd=\nHost_address=\nHost_port="
            userini = open("users.ini", "w")
            userini.write(contenu)
            userini.close()

        with open("users.ini", "r") as users_ini:
            for ligne in users_ini:
                key, valeur = ligne.strip().split("=")
                self.dic_users[key] = valeur
                self.dic_users.update(self.dic_users)
            self.db_user = self.dic_users["DB_user"]
            self.db_passwd = self.dic_users["DB_passwd"]
            self.login_user = self.dic_users["Login_user"]
            self.login_passwd = self.dic_users["Login_passwd"]
            self.host_address = self.dic_users["Host_address"]
            self.host_port = self.dic_users["Host_port"]

# Creation du fichier config.ini pour la restauration
    def config_ini(self):
        if not os.path.isfile(self.path_dossier_config + "config.ini"):
            contenu = "Dossier_cible=" + self.dossier_backup + "/" + "\nDossier_annee=" + str(self.dossier_annee) + \
                      "\nDossier_config=" + self.path_dossier_config
            confini = open(self.path_dossier_config + "config.ini", "w")
            confini.write(contenu)
            confini.close()

    def lecture_derniere_exec(self):

        with open(self.path_dossier_config + "derniere_execution", "r") as derniere_exec:
            for ligne in derniere_exec:
                key, valeur = ligne.strip().split("=")
                self.dic_rotation[key] = valeur
                self.dic_rotation.update(self.dic_rotation)

    def derniere_execution(self):
        if os.path.isfile(self.path_dossier_config + "derniere_execution"):
            self.dic_rotation = {}
            self.lecture_derniere_exec()
            self.exec_jour = int(self.dic_rotation["jour_de_lannee"])

            if self.jour_de_lannee - self.exec_jour == 0:
                # Sauvegarde incrementielle le même jour

                self.indice = str(self.dic_rotation["indice"])
                self.indice_jour = (int(self.dic_rotation["indice_jour"]) + 1)
                self.type = "I"
                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + str(self.indice_jour) + "_"\
                                      + str(self.format_date) + ".tar.gz"
                self.fichier_derniere_exec()

            if self.jour_de_lannee - self.exec_jour == 1:
                # Sauvegarde incrementielle de la veille voir backup()

                if int(self.dic_rotation["indice"]) == 7:
                    self.indice = 1
                    self.type = "C"
                else:
                    self.indice = (int(self.dic_rotation["indice"]) + 1)
                    self.type = "I"

                self.indice_jour = 0
                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)\
                                      + ".tar.gz"
                self.nom_dir_mariabd = "{}mariadb_full/".format(self.path_du_jour)
                self.fichier_derniere_exec()

            if 1 < self.jour_de_lannee - self.exec_jour <= 7:

                decalage = self.jour_de_lannee - self.exec_jour
                self.indice_jour = 0

                if (int(self.dic_rotation["indice"]) + decalage) < 7:
                    self.indice = (int(self.dic_rotation["indice"]) + decalage)
                    self.type = "I"
                else:
                    self.indice = 1
                    self.type = "C"

                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)\
                                      + ".tar.gz"
                self.fichier_derniere_exec()

            if self.jour_de_lannee - self.exec_jour > 7:
                print("plus d'une semaine")

                self.type = "C"
                self.indice = 1
                self.indice_jour = 0
                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)\
                                      + ".tar.gz"
                self.fichier_derniere_exec()
        else:
            self.indice = 1
            self.type = "C"
            self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)\
                                  + ".tar.gz"
            self.fichier_derniere_exec()

    def fichier_derniere_exec(self):

        contenu = "jour=" + self.jour_semaine + "\njour_de_lannee=" + str(self.jour_de_lannee) + "\nNo_semaine=" \
                  + str(self.numero_semaine) + "\nNo_jour_semaine=" + str(self.numero_jour_semaine) + \
                  "\nindice="+str(self.indice) + "\nindice_jour=" + str(self.indice_jour) + "\ntype=" + self.type

        derniere_exec = open(self.path_dossier_config + "derniere_execution", "w")
        derniere_exec.write(contenu)
        derniere_exec.close()
        self.backup()

    def fichier_log(self):
        self.message_log = self.format_date + " - " + self.message_log
        fichier_log = open(self.path_dossier_config + "backup.log", "a")
        fichier_log.write(self.message_log + "\n")
        fichier_log.close()

    def backup(self):
        self.creation_fichier_quot()
        self.lecture_derniere_exec()

        if self.type == "C" and self.indice == 1:

            try:
                os.remove(self.dossier_backup + "/" + self.fichier_snar)
            except (OSError, Exception):
                self.message_log = "Avertissement :  le fichier : " + self.fichier_snar + \
                                   " est absent ou inacessible - Premiere exécution ?"
                self.fichier_log()

            self.dossier_local()
            self.suppression_fichiers()
            self.tar()
            self.mariadb_full()
            self.hebdomadaire()

        if self.type == "I":
            # Sauvegarde incrementielle
            if self.indice_jour >= 1:
                # incrementielle du meme jour
                self.dossier_local()
                self.message_log = "Avertissement : Sauvegarde incrementielle le même jour: " + self.jour_semaine + "/"\
                                   + self.nom_de_fichier
                self.nom_dir_mariabd = "{}mariadb_inc{}/\n".format(self.path_du_jour, self.indice_jour)
                self.creation_fichier_maria()
                self.fichier_log()
                self.tar()
                self.mariadb_increment()
            else:
                # sauvegarde incrementielle
                self.path_du_jour = self.dossier_backup + "/" + str(self.dossier_annee) + "/" + "quotidienne/" \
                                    + self.jour_semaine + "/"
                self.message_log = "Information : Sauvegarde incrementielle : " + self.jour_semaine + "/" \
                                   + self.nom_de_fichier
                self.nom_dir_mariabd = "{}mariadb_inc/\n".format(self.path_du_jour)
                self.creation_fichier_maria()
                self.fichier_log()
                self.dossier_local()
                self.suppression_fichiers()
                self.tar()
                self.mariadb_increment()
            print("on copie l'increment du jour")

    def tar(self):

        commande = "tar -cpz --listed-incremental={}/{} --file={}{} {} >/dev/null 2>&1"\
            .format(self.dossier_backup, self.fichier_snar, self.path_du_jour, self.nom_de_fichier, self.dossier_source)

        if sys.platform.startswith("linux"):
            os.system(commande)
        else:
            print(commande)

    def hebdomadaire(self):
        self.path_hebdomadaire = (self.dossier_backup + "/" + self.dossier_annee + "/" + "hebdomadaire/"
                                  + "S" + str(self.numero_semaine) + "/")
        if not os.path.isdir(self.path_hebdomadaire):
            os.makedirs(self.path_hebdomadaire)
            self.copy_archives()

    def copy_archives(self):
        commande = "tar -cpz --file {}mariadb_full_{}.tar.gz {}mariadb_full"\
            .format(self.path_hebdomadaire, self.format_date, self.path_du_jour)
        if sys.platform.startswith("linux"):
            shutil.copyfile(self.path_du_jour + self.nom_de_fichier, self.path_hebdomadaire + self.nom_de_fichier)
            os.system(commande)

        else:
            print("Copie de {}{} vers {}".format(self.path_du_jour, self.nom_de_fichier, self.path_hebdomadaire))
            print(commande)
        self.liste_hebdo()

    def liste_hebdo(self):
        contenu_hebdo = "{}mariadb_full_{}.tar.gz".format(self.path_hebdomadaire, self.format_date) + ","\
                        + self.path_hebdomadaire + self.nom_de_fichier
        resto_hebdo = open(self.path_dossier_config + "hebdomadaire", "a")
        resto_hebdo.write(contenu_hebdo)
        resto_hebdo.close()

    def mariadb_increment(self):
        self.mariadb_path_to_full()
        commande = "mariabackup --backup --target_dir={}mariadb_inc{}/ --incremental-basedir={} --user={}" \
                   " --password={}  >/dev/null 2>&1".format(self.path_du_jour, self.indice_jour,
                                                            self.mariabd_full_path, self.db_user, self.db_passwd)

        self.message_log = "Information : Creation d'un backup incremental mariadb dans mariadb_inc{}"\
            .format(self.indice_jour)
        self.fichier_log()

        if sys.platform.startswith("linux"):
            os.system(commande)
        else:
            print(commande)

    def mariadb_full(self):
        self.mariadb_path_to_full()
        commande = "mariabackup --backup --target-dir={}mariadb_full/ --user={} --password={} >/dev/null 2>&1"\
            .format(self.path_du_jour, self.db_user, self.db_passwd)

        self.nom_dir_mariabd = "{}mariadb_full/\n".format(self.path_du_jour)
        self.creation_fichier_maria()

        self.message_log = "Information : Creation d'un backup full mariadb dans {}".format(self.mariabd_full_path)
        self.fichier_log()

        if sys.platform.startswith("linux"):
            os.system(commande)
        else:
            print(commande)

    def mariadb_path_to_full(self):

        with open(self.path_dossier_config + "quotidienne") as fichier_quot:
            full_bckup = list(islice(fichier_quot, 1))
            la_liste = (str(full_bckup[0]).split("_"))
            self.mariabd_full_path = self.dossier_backup + "/" + str(self.dossier_annee) + "/" + "quotidienne" + "/"\
                                     + str(la_liste[1]) + "/mariadb_full/"

    def dossier_local(self):
        self.path_du_jour = self.dossier_backup + "/" + str(self.dossier_annee) + "/" + "quotidienne/"\
                            + self.jour_semaine + "/"
        try:
            os.makedirs(self.path_du_jour)
            #self.dossier_distant()
            self.message_log = "Information : creation du dossier " + self.jour_semaine
            self.fichier_log()
        except OSError:
            if self.indice_jour == 0:
                self.message_log = "Information : Le dossier " + self.jour_semaine +\
                                   " existe -> suppression des fichiers"
                self.fichier_log()

    def suppression_fichiers(self):
        pattern_dossier = "mariadb_"
        pattern_fichier = "sauv_"
        try:
            for element in os.listdir(self.path_du_jour):
                if pattern_fichier in element:
                    os.remove(self.path_du_jour + element)
                if pattern_dossier in element:
                    shutil.rmtree(self.path_du_jour + element)

        except IOError:
            self.message_log = "Erreur : Le dossier " + self.path_du_jour + " n'existe pas ou n'est pas accessible"
            self.fichier_log()

    def creation_fichier_quot(self):
        contenu_fichier = self.nom_de_fichier + self.nom_dir_mariabd + "\n"
        fichier_resto = open(self.path_dossier_config + "quotidienne", "a")
        fichier_resto.write(contenu_fichier)
        fichier_resto.close()

    def creation_fichier_maria(self):
        contenu_fichier_maria = self.nom_dir_mariabd
        mariadb_resto = open(self.path_dossier_config + "mariadb", "a")
        mariadb_resto.write(contenu_fichier_maria)
        mariadb_resto.close()

    def dossier_distant(self):
        sftp = pysftp.Connection(self.host_address, username=self.login_user, password=self.login_passwd)
        sftp.makedirs(self.remote_base + self.path_du_jour)
        sftp.close()
        self.copy_pysftp()

    def suppr_dossier_distant(self):

        commande = "rm -R {}{}/quotidienne/{}/*".format(self.remote_base, str(self.dossier_annee), self.jour_semaine)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host_address, self.host_port, self.login_user, self.login_passwd)
        ssh.exec_command(commande)

    def copy_pysftp(self):
        print(self.dossier_backup + " vers " + self.remote_base)
        self.suppr_dossier_distant()
        sftp = pysftp.Connection(self.host_address, username=self.login_user, password=self.login_passwd)
        sftp.put_r(self.dossier_backup, self.remote_base, preserve_mtime=True)
        sftp.close()

    def initialisation(self):
        if not os.path.isdir(self.dossier_backup):
            return False


test = GestionFichier()
