# -*- coding: utf-8 -*-


class Restauration:
    def __init__(self):
        self.lecture_quotidienne()
        self.liste = []
        self.key = ""
        self.en_clair = ""
        self.jour = ""
        self.dic_config = {}

    def lecture_quotidienne(self):
        with open('quotidienne') as resto_quot:
            self.liste = dict(enumerate(line.strip() for line in resto_quot))
            print(" N°   Jour  Date        Heure      Complète / Incrementielle")
        for i in range(0, len(self.liste)):

            self.jour = str(self.liste[i]).split("_")
            self.en_clair = self.jour[1] + " " + self.jour[5] + "/" + self.jour[4] + "/" + self.jour[3] + " "\
                            + " " + self.jour[6] + ":" + self.jour[7] + ":" + self.jour[8] + " - type : " + self.jour[2]
            print("[" + str(i) + "]" + " - " + self.en_clair)

        self.restauration()

    def restauration(self):
        la_condition = True
        while la_condition:
            self.key = input("Indiquez le numéro de sauvegarde à restaurer, 'q' pour quitter : ")

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
                print("on quitte")
                quit()

        print("on fait le job")
        self.routine_resto_complete()

    def routine_resto_complete(self):
        self.dic_config = {}
        with open("config.ini", "r") as confini:
            for ligne in confini:
                key, valeur = ligne.strip().split("=")
                self.dic_config[key] = valeur
                self.dic_config.update(self.dic_config)

        for y in range(0, int(self.key) + 1):
            print(self.dic_config["Dossier_cible"] + "/" + str(self.jour[3]) + "/" + str(self.jour[1]) + "/"
                  + str(self.liste[y]))


test = Restauration()
