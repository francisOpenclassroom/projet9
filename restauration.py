# -*- coding: utf-8 -*-


class Restauration:
    def __init__(self):
        self.lecture_quotidienne()
        self.liste = []
        self.key = ""
        self.en_clair = ""

    def lecture_quotidienne(self):
        with open('quotidienne') as resto_quot:
            self.liste = dict(enumerate(line.strip() for line in resto_quot))
        print(self.liste)
        print(len(self.liste))
        for i in range(0, len(self.liste)):

            jour = str(self.liste[i]).split("_")
            self.en_clair = jour[1] + " " + jour[5] + "/" + jour[4] + "/" + jour[3] + " " + " " + jour[6] + \
                       ":" + jour[7] + ":" + jour[8] + " - type : " + jour[2]
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
        for y in range(0, int(self.key) + 1):
            print(y, self.liste[y])







            # try:
            #     if int(key) > len(self.liste):
            #         print("choix invalide")
            #         quit()
            # except:
            #     print("choix invalide")
            #     quit()
        # try:
        #     for y in range(0, int(key) + 1):
        #         print(y, self.liste[y])
        # except KeyError:
        #     print("Choix invalide")
        #     quit()
        # except ValueError:
        #     print("Choix invalide")
        #     quit()




test = Restauration()
