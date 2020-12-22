# -*- coding: utf-8 -*-

import locale
import datetime

import os
locale.setlocale(locale.LC_TIME, '')

# TODO: gérer un fichier pour la restauration dans le dossier source quotidienne
# TODO: gérer la sauvegare complète et incrémentielle de mariadb avec maribackup
# TODO: vérifier la sauvegarde complète et générer les fichiers tar correspondants


class GestionFichier:
    def __init__(self):
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
        self.dossier_annee = str(annee)
        self.fichier_snar = "backup.snar"
        self.dossier_source = "Dossier_Source"
        self.path_local = os.getcwd()
        self.dic_rotation = {}
        self.derniere_execution()
        self.creation_fichier()

    def lecture_derniere_exec(self):

        with open("derniere_execution", "r") as derniere_exec:
            for ligne in derniere_exec:
                key, valeur = ligne.strip().split("=")
                self.dic_rotation[key] = valeur
                self.dic_rotation.update(self.dic_rotation)

    def derniere_execution(self):
        if os.path.isfile("derniere_execution"):
            self.dic_rotation = {}
            self.lecture_derniere_exec()
            self.exec_jour = int(self.dic_rotation["jour_de_lannee"])

            if self.jour_de_lannee - self.exec_jour == 0:
                # Sauvegarde incrementielle le même jour

                self.indice = str(self.dic_rotation["indice"])
                self.indice_jour = (int(self.dic_rotation["indice_jour"]) + 1)
                self.type = "I"
                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + str(self.indice_jour) + "_"\
                                      + str(self.format_date)
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
                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)
                print("le nome de fichier est " + self.nom_de_fichier)
                self.fichier_derniere_exec()

            if 1 < self.jour_de_lannee - self.exec_jour <= 7:
                print("plus d'un jour mais dans la meme semaine")

                decalage = self.jour_de_lannee - self.exec_jour
                self.indice_jour = 0

                if (int(self.dic_rotation["indice"]) + decalage) < 7:
                    self.indice = (int(self.dic_rotation["indice"]) + decalage)
                    self.type = "I"
                else:
                    self.indice = 1
                    self.type = "C"

                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)
                print(self.nom_de_fichier)
                self.fichier_derniere_exec()

            if self.jour_de_lannee - self.exec_jour > 7:
                print("plus d'une semaine")

                self.type = "C"
                self.indice = 1
                self.indice_jour = 0
                self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)
                print(self.nom_de_fichier)
                self.fichier_derniere_exec()
        else:
            self.indice = 1
            self.type = "C"
            self.nom_de_fichier = "sauv_" + str(self.jour_semaine) + "_" + self.type + "_" + str(self.format_date)
            self.fichier_derniere_exec()

    def fichier_derniere_exec(self):

        contenu = "jour=" + self.jour_semaine + "\njour_de_lannee=" + str(self.jour_de_lannee) + "\nNo_semaine=" \
                  + str(self.numero_semaine) + "\nNo_jour_semaine=" + str(self.numero_jour_semaine) + \
                  "\nindice="+str(self.indice) + "\nindice_jour=" + str(self.indice_jour) + "\ntype=" + self.type

        derniere_exec = open("derniere_execution", "w")
        derniere_exec.write(contenu)
        derniere_exec.close()
        self.backup()

    def fichier_log(self):
        self.message_log = self.format_date + " - " + self.message_log
        fichier_log = open("backup.log", "a")
        fichier_log.write(self.message_log + "\n")
        fichier_log.close()

    def backup(self):
        print()
        self.lecture_derniere_exec()
        if self.type == "C" and self.indice == 1:

            try:
                os.remove(self.dossier_backup + "/" + self.fichier_snar)
            except FileNotFoundError:
                self.message_log = "Erreur :  le fichier : " + self.fichier_snar + " est absent ou inacessible"
                print(self.message_log)
                self.fichier_log()

            self.dossier_local()
            self.suppression_fichiers()
            print("on créé un backup complet + snar dans le dossier jour local")
            self.tar()
            print("on copie le backup dans le dossier de la semaine pour rotation")

        if self.type == "I":
            # Sauvegarde incrementielle
            if self.indice_jour >= 1:
                # incrementielle du meme jour
                self.dossier_local()
                self.message_log = "Avertissement : Sauvegarde incrementielle le même jour: " + self.jour_semaine + "/"\
                                   + self.nom_de_fichier
                self.fichier_log()
                self.tar()
                self.dump_mysql()
            else:
                # sauvegarde incrementielle
                self.path_du_jour = self.dossier_backup + "/" + str(self.dossier_annee) + "/" + "quotidienne/" \
                                    + self.jour_semaine + "/"
                self.message_log = "Information : Sauvegarde incrementielle : " + self.jour_semaine + "/" \
                                   + self.nom_de_fichier
                print("dans backup : " + self.nom_de_fichier)
                self.fichier_log()
                self.dossier_local()
                self.suppression_fichiers()
                self.tar()
                self.dump_mysql()
            print("on copie l'increment du jour")

    def tar(self):

        commande = "tar -c --listed-incremental={}/{} --file={}{} {}"\
            .format(self.dossier_backup, self.fichier_snar, self.path_du_jour, self.nom_de_fichier, self.dossier_source)
        print(commande)

    def dump_mysql(self):
        if self.type == "I":
            print("sauvegarde incrementielle mariadb")
        else:
            print("sauvegarde complete mariadb")

    def dossier_local(self):
        self.path_du_jour = self.dossier_backup + "/" + str(self.dossier_annee) + "/" + "quotidienne/"\
                            + self.jour_semaine + "/"
        try:
            os.makedirs(self.path_du_jour)
            self.message_log = "Information : creation du dossier " + self.jour_semaine
            self.fichier_log()
        except OSError:
            if self.indice_jour == 0:
                self.message_log = "Information : Le dossier " + self.jour_semaine +\
                                   " existe -> suppression des fichiers"
                self.fichier_log()

    def suppression_fichiers(self):
        print(self.path_du_jour)

        try:
            for fichier in os.listdir(self.path_du_jour):
                os.remove(self.path_du_jour + fichier)
        except FileNotFoundError:
            self.message_log = "Erreur : Le dossier " + self.path_du_jour + " n'existe pas ou n'est pas accessible"
            self.fichier_log()

    def creation_fichier(self):

        contenu_fichier = self.nom_de_fichier +"\n"
        fichier_resto = open("quotidienne", "a")
        fichier_resto.write(contenu_fichier)
        fichier_resto.close()


test = GestionFichier()
