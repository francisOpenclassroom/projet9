# projet9

Ces script sont destinés à la sauvegarde et la restauration d'un serveur Wordpress et d'une base de données mariadb. Il permet d'assurer une sauvegarde quotidienne ainsi qu'un archivage heddmomaire.

Le contenu des sauvegardes est téléchargé vers un serveur de sauvegarde avec le protocole SFTP.

# prérequis :

Les machines doivent être configurés pour être accéssibles en SFTP et SSH pour les utilisateurs systèmes renseignés.
Les module python Pysftp et par extension paramiko doit être installé dans Python, prévoir donc l'installation de PIP sur les deux machines.


# rotation_backup.py

Il s'agit du module de sauvegarde à installer sur le seveur de producation (worpdress) le dossier configuré par défaut est /var/rotation_backup.
Lors de la première exécution, un fichier users.ini est généré et doit être renseingé avec les identifiants nécessaires à la connexion au serveur avec les droits appropriés (Ecriture dans le dossier /var/.
Il est également nécessaire de saisir un identifiant et un mot de passe pour un utilisateur autorisé à effectuer une sauvegarde de la base de donnéees Mariadb.
Il faut enfin, renseigner les informations de connexion (ip/port) pour les service SFTP.

# restauration.py

Il s'agit du module de restauration des données à installer sur le serveur de sauvegarde. Lors de la première exécution un fichier resto.ini est généré, il est nécessaire de renseigner avec les identifiantsde connexion à la base données ainsi qu'à un compte autorisé à créer des dossiers dans /var/.
