# -*- coding: utf-8 -*-


import locale
import sys
import paramiko
import pysftp
import linecache
import os

if sys.platform.startswith("darwin"):

    locale.setlocale(locale.LC_ALL, 'fr_FR')
else:
    locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')


class Restauration:
    def __init__(self):

        # "/var/rotation_backup
        self.dossier_cible = ""
        # "/var/rotation_backup"
        self.dossier_mariadb = ""
        self.host_address = ""
        self.host_port = 0
        self.login_user = ""
        self.login_passwd = ""

        self.liste = []
        self.key = 0
        self.en_clair = ""
        self.jour = ""
        self.dic_config = {}
        self.liste_mariadb = []
        self.chemin_config = ""
        self.dossier_source = ""
        self.mariadb = ""
        self.commande_tar = ""
        self.stop_mariadb = ""
        self.supp_mysql = ""
        self.prepa_mariadb = ""
        self.restauration_mariadb = ""
        self.synchro_mariadb = ""
        self.acl_mariadb = ""
        self.start_mariadb = ""
        self.restart_host = ""
        self.dic_users = {}
        self.resto_ini()
        self.lecture_config()
        self.copie_backup()
        self.lecture_mariadb()
        self.lecture_quotidienne()

    def resto_ini(self):
        if not os.path.isfile("resto.ini"):
            contenu = "Login_user=\nLogin_passwd=\nHost_address=\nHost_port=\ndossier_cible=\ndossier_mariadb="
            restoini = open("resto.ini", "w")
            restoini.write(contenu)
            restoini.close()
            print("Le fichier ini est absent, merci de le renseigner")
            quit()
        with open("resto.ini", "r") as resto_ini:
            for ligne in resto_ini:
                key, valeur = ligne.strip().split("=")
                self.dic_users[key] = valeur
                self.dic_users.update(self.dic_users)
            self.login_user = self.dic_users["Login_user"]
            self.login_passwd = self.dic_users["Login_passwd"]
            self.host_address = self.dic_users["Host_address"]
            self.host_port = self.dic_users["Host_port"]
            self.dossier_cible = self.dic_users["dossier_cible"]
            self.dossier_mariadb = self.dic_users["dossier_mariadb"]

    def copie_backup(self):
        self.dossier_cible = self.dossier_cible + "/" + self.dossier_source
        sftp = pysftp.Connection(self.host_address, username=self.login_user, password=self.login_passwd)
        sftp.makedirs(self.dossier_cible)
        sftp.put_r(self.dossier_source, self.dossier_cible, preserve_mtime=True)
        sftp.close()
        print "copie de : " + self.dossier_source + " vers " + self.dossier_cible

    def lecture_config(self):

        self.dic_config = {}
        with open("backup/config/config.ini", "r") as confini:
            for ligne in confini:
                key, valeur = ligne.strip().split("=")
                self.dic_config[key] = valeur
                self.dic_config.update(self.dic_config)
        self.chemin_config = self.dic_config["Dossier_config"]
        self.dossier_source = self.dic_config["Dossier_cible"]

    def lecture_mariadb(self):

        with open(self.chemin_config + "mariadb", "r") as mariadb_file:
            self.liste_mariadb = mariadb_file.read().splitlines()

    def lecture_quotidienne(self):

        with open(self.chemin_config + "quotidienne", "r") as resto_quot:
            self.liste = dict(enumerate(line.strip() for line in resto_quot))
            print(" N°   Jour  Date        Heure      Complète / Incrementielle")
        for i in range(0, len(self.liste)):
            self.mariadb = str(self.liste_mariadb[i]).split("/")
            self.jour = str(self.liste[i]).split("_")
            self.en_clair = self.jour[1] + " " + self.jour[5] + "/" + self.jour[4] + "/" + self.jour[3] + " "\
                            + " " + self.jour[6] + ":" + self.jour[7] + ":" + self.jour[8] + " - type : " + self.jour[2]
            print("[" + str(i) + "]" + " - " + self.en_clair + "\t \t " + self.mariadb[4])

        self.restauration()

    def restauration(self):
        la_condition = True
        while la_condition:
            self.key = raw_input("Indiquez le numéro de sauvegarde à restaurer, 'q' pour quitter : ")
            try:
                if int(self.key) > len(self.liste) - 1:
                    print("au dessus")
                    la_condition = True
                else:
                    la_condition = False
            except ValueError:
                la_condition = True
                if self.key.lower() == "q":
                    la_condition = False
                    quit()

        print("on fait le job")

        self.routine_resto_complete()

    def routine_resto_complete(self):

        onyva = True
        while onyva:

            print("Restauration de : " + str(self.liste[int(self.key)]) + "\t" + str(self.liste_mariadb[int(self.key)]))
            confirmation = raw_input("Etes vous sur de vouloir continuer  O/N - ? : ")
            if confirmation == "O":
                onyva = False
            if confirmation == "N":
                quit()

        self.resto_tar()

    def resto_tar(self):

        for y in range(0, int(self.key) + 1):
            lignes = linecache.getline(self.chemin_config + "quotidienne", y + 1)
            fichier_tar = (self.dossier_cible + lignes.split("_")[3] + "/" + "quotidienne/" + lignes.split("_")[1] + "/"
                           + str(self.liste[y]))
            print "restauration de : " + fichier_tar
            self.commande_tar = "tar -vxzf " + fichier_tar + " -C /"
            self.execution_distante(self.commande_tar)
        self.resto_mariadb()

    def resto_mariadb(self):
        print("Arret du service mariadb")
        self.stop_mariadb = "systemctl stop mariadb"
        self.execution_distante(self.stop_mariadb)
        print self.stop_mariadb

        print("Suppresion du dossier mysql")
        self.supp_mysql = "rm -R /var/lib/mysql/"
        self.execution_distante(self.supp_mysql)
        print self.supp_mysql

        if int(self.key) == 0:
            print("FULL")

            print("Préparation de la restauration de la BDD")
            print(self.dossier_cible)
            self.prepa_mariadb = "mariabackup --prepare --target-dir={}/{}"\
                .format(self.dossier_mariadb, self.liste_mariadb[int(self.key)])
            self.execution_distante(self.prepa_mariadb)
            print self.prepa_mariadb

            print("Restauration de la BDD")
            self.restauration_mariadb = "mariabackup --copy-back --target-dir={}/{}"\
                .format(self.dossier_mariadb, self.liste_mariadb[int(self.key)])
            self.execution_distante(self.restauration_mariadb)
            print self.restauration_mariadb

        else:
            print("INCREMENTALE")
            print("Préparation de la restauration de la BDD")
            self.prepa_mariadb = "mariabackup --prepare --target-dir={}/{}"\
                .format(self.dossier_mariadb, self.liste_mariadb[0])
            self.execution_distante(self.prepa_mariadb)
            print self.prepa_mariadb

            print"Synchronisation des incréments"
            for y in range(1, int(self.key) + 1):
                # print y
                # lignes = linecache.getline(self.chemin_config + "mariadb", y + 1)
                # print lignes
                self.synchro_mariadb = "mariabackup --prepare --target-dir={}/{} --incremental-dir={}/{}"\
                    .format(self.dossier_mariadb, self.liste_mariadb[0], self.dossier_mariadb, self.liste_mariadb[y])
                self.execution_distante(self.synchro_mariadb)
                print self.synchro_mariadb

            print("Restauration de la BDD")
            self.restauration_mariadb = "mariabackup --copy-back --target-dir={}/{}"\
                .format(self.dossier_mariadb, self.liste_mariadb[0])
            self.execution_distante(self.restauration_mariadb)
            print self.restauration_mariadb

        print("Correction des ACL")
        self.acl_mariadb = "chown -R mysql:mysql /var/lib/mysql/"
        self.execution_distante(self.acl_mariadb)
        print self.acl_mariadb

        print("démarrage de mariadb")
        self.start_mariadb = "systemctl start mariadb"
        self.execution_distante(self.start_mariadb)
        print self.start_mariadb

        print("reboot")
        self.restart_host = "reboot"
        self.execution_distante(self.restart_host)
        print self.restart_host

    def execution_distante(self, commande):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host_address, self.host_port, self.login_user, self.login_passwd)
        stdin, stdout, stderr = ssh.exec_command(commande)
        lignes = stderr.readlines()
        for err_msg in range(len(lignes)):
            print(lignes[err_msg])


resto = Restauration()
