import pysftp

sftp = pysftp.Connection('192.168.1.60', username='root', password='francis1965')
sftp.cwd("/var/")
print(sftp.pwd)
sftp.close()
