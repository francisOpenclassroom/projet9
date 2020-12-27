# -*- coding: utf-8 -*-
# TODO : Copier le fichier config.ini à la racine pendant lors du transfert distant

import locale
import os
import sys

if sys.platform.startswith("darwin"):

    locale.setlocale(locale.LC_ALL, 'fr_FR')
else:
    locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

class Restauration:
    def __init__(self):

        self.liste = []
        self.key = 0
        self.en_clair = ""
        self.jour = ""
        self.dic_config = {}
        self.liste_mariadb = []
        self.chemin_backup = ""
        self.mariadb = ""
        self.lecture_config()
        self.lecture_mariadb()
        self.lecture_quotidienne()

    def lecture_config(self):

        self.dic_config = {}
        with open("config.ini", "r") as confini:
            for ligne in confini:
                key, valeur = ligne.strip().split("=")
                self.dic_config[key] = valeur
                self.dic_config.update(self.dic_config)
        self.chemin_backup = self.dic_config["Dossier_config"]

    def lecture_mariadb(self):

        with open(self.chemin_backup + "mariadb", "r") as mariadb_file:
            self.liste_mariadb = mariadb_file.read().splitlines()



    def lecture_quotidienne(self):

        with open(self.chemin_backup + "quotidienne", "r") as resto_quot:
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
        # while la_condition:
            # lakey = ("Indiquez le numéro de sauvegarde à restaurer, 'q' pour quitter : ")
            # self.key = int(lakey)

            # try:
            #     if int(self.key) > len(self.liste) - 1:
            #         print("au dessus")
            #         la_condition = True
            #     else:
            #         la_condition = False
            # except ValueError:
            #     la_condition = True
            #
            # if self.key.lower() == "q":
            #     la_condition = False
            #     print("on quitte")
            #     quit()

        print("on fait le job")

        self.routine_resto_complete()

    def routine_resto_complete(self):

        onyva = True
        while onyva:
            #print("Restauration du fichier : " + str(self.liste[int(self.key)]) + str(self.mariadb[int(self.key)]))
            print("Restauration de : " + str(self.liste[int(self.key)]) + "\t" + str(self.liste_mariadb[int(self.key)]))
            confirmation = input("Etes vous sur de vouloir continuer  O/N - ? : ")
            if confirmation == "O":
                onyva = False
            if confirmation == "N":
                quit()

        # for y in range(0, int(self.key) + 1):
        #     print(self.dic_config["Dossier_cible"] + str(self.jour[3]) + "/" + str(self.jour[1]) + "/"
        #           + str(self.liste[y]) + "\t" + self.liste_mariadb[y])
        self.resto_tar()
    def resto_tar(self):

        for y in range(0, int(self.key) + 1):
            fichier_tar = (self.dic_config["Dossier_cible"] + str(self.jour[3]) + "/" + str(self.jour[1]) + "/"
                  + str(self.liste[y]))

            commande = "tar -xzf " + fichier_tar + " -C /"

            if sys.platform.startswith("linux"):
                os.system(commande)
            else:
                print(commande)


test = Restauration()
