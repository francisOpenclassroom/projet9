import locale
import subprocess
import datetime
import pysftp
import os

# defintion des elements de date et jour

locale.setlocale(locale.LC_TIME,'')
jour = datetime.datetime.now()
aujourdhui = (jour.strftime("%A"))
la_date = (jour.strftime("%d_%m_%y"))


# declaration des variables

dossier_source = "/var/www/html/wordpress/"
dossier_cible = "/home/francis/backup/"
fichier_cible = "backup_" + aujourdhui + "_" + la_date + ".tar"
dump_cible = "dump_worpress_" + aujourdhui + "_" + la_date + ".sql"
dossier_jour = dossier_cible+aujourdhui+"/"
fichier_snapshot = "backup.snar"

remote_dir = "/home/francis/backup/"

class FichierInit:
	def __init__(self):
		self.fichier_init = dossier_cible + "init"
		self.jour_backup = aujourdhui


		print self.jour_backup






# gestion des dossiers locaux

if not os.path.exists(dossier_jour):
	os.makedirs(dossier_jour)



# test de la sauvegarde hedbomadaire

if jour == "lundi" and day_of_month <= 7:
    print "c'est  le premier Lundi du mois"
else:
    print "ce n'est pas le premier lundi du mois"


# execution des commmandes de sauvegarde

os.system("tar -c --listed-incremental={}{} --file={}{} {}".format(dossier_jour, fichier_snapshot, dossier_jour, fichier_cible, dossier_source))
os.system("mysqldump --user=user1 --password=francis1965 --result-file='{}{}' wordpress".format(dossier_jour, dump_cible))


# transfert des fichiers par SFTP

sftp = pysftp.Connection('192.168.1.60', username='root', password='francis1965')


# Gestion des dossiers distants

if sftp.isdir(remote_dir + aujourdhui):

	print "le dossier_backup_existe"

else :
	print "le dossier n'existe pas"
	sftp.makedirs(remote_dir+aujourdhui)


sftp.put_d(dossier_jour, remote_dir+aujourdhui)

sftp.close()



FichierInit()

