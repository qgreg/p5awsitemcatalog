Provisioning a Webserver
========================

This project uses the application developed in Project 3 to configure a web server to deplay the appliation. Using a virtual server in Amazon’s Elastic Compute Cloud (EC2), the web server runs a stack of Linux, Apache, PostgreSQL and Python to serve and run the application. 

While the project is available during grading, this is the project's URL:
http://ec2-52-27-221-22.us-west-2.compute.amazonaws.com/

*Configuring the Server* details the steps taken to confure the server and provides source references for the steps taken.

### Exceeding Specifications
The project seeks to exceed specifications by implementing the following.
1. Fail2ban monitors for repeat unsuccessful login attempts and appropriately bans attackers.
2. *** automatically manages package updates
3. Glances provides automatic feedback on appliation availability status.
Details on these features are included in *Configuring the Server*.


Configuring the Server
----------------------

### Helpful tips

Always have two terminal windows open. When you test changes you have made, this can help you keep from being locked out.

## Logging on to the Instance

1. Download Private Key from the Udacity website
2. Move the private key file into the folder ~/.ssh (where ~ is your environment's home directory). So if you downloaded the file to the Downloads folder, just execute the following command in your terminal.
```
mv ~/Downloads/udacity_key.rsa ~/.ssh/
```
3. Open your terminal and type in
```
chmod 600 ~/.ssh/udacity_key.rsa
```
In your terminal, type in
```
ssh -i ~/.ssh/udacity_key.rsa root@52.11.199.213
```

Reference: https://www.udacity.com/account#!/development_environment 


## Adding New User
To add the user grader:
```
sudo adduser grader
```
Adduser requires a passworda and allows for user optional information.

Reference: https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4331066009/m-4801089468


## Giving grader sudo access

To add sduo access, create the following file and add the language below:
```
touch /etc/sudoers.d/grader
sudo nano /etc/sudoers.d/grader
```
Add the following line to the file /etc/sudoers.d/grader:
```
grader ALL=(ALL) NOPASSWD:ALL
```
Save and close nano.

Reference: https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4331066009/m-4801089471


## Securing New User

Switch your user to grader
```
su grader
```
Go to the home directory
```
cd
```
Make a .ssh directory
```
mkdir .ssh
```
Create a key locally.
```
ssh-keygen
```
Provide a password for the key file. Save the file locally in the home .ssh file. Copy the key from your local file to the file /home/grader/.ssh/authorized_keys

Put property security in place:
```
chmod 700 ~/.ssh
chmod 644 ~/.ssh/authorized_keys
```

Reference: https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4331066009/m-4801089481


## Disable remote root login and enforce key-based authentication

Edit the configuration file:
```
sudo nano /etc/ssh/sshd_config
```
Change the PermitRootLogin and PasswordAuthentication as follows:
```
PermitRootLogin no
PasswordAuthentication no
```

Reference: http://askubuntu.com/questions/27559/how-do-i-disable-remote-ssh-login-as-root-from-a-server


## Updating Software

"""
sudo apt-get update
sudo apt-get upgrade
"""
Answer yes to the question.
"""
sudo apt-get autoremove
"""

Reference: https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4331066009/m-4801089452
https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4331066009/m-4801089453
https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4331066009/m-4801089454


## Configure timezone to UTC

The following program updates the time configuration:
"""
sudo dpkg-reconfigure tzdata
"""
Select None of the above and UTC.

Reference: http://unix.stackexchange.com/questions/110522/timezone-setting-in-linux


## Change ssh Port to 2222

```
sudo nano /etc/ssh/sshd_config
```
Change the text as follows:
```
# What ports, IPs and protocols we listen for
Port 2200
```
Then restart ssh
```
sudo service ssh restart
```

Reference: http://ubuntuforums.org/showthread.php?t=1591681


## Configure Firewall

```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2200/tcp
sudo ufw allow www
sudo ufw allow ntp
```
Check your work with:
```
sudo ufw show added
```

Once you have confirmed that the configuration is correct, start the firewall:
```
sudo ufw enable
```

Reference
https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4331066009/m-4801089499
Preparing UFW
https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands
sudo ufw show added
http://askubuntu.com/questions/30781/see-configured-rules-even-when-inactive


## Monitoring Unsuccessful Logins

Install fail2ban
```
sudo apt-get install fail2ban
```
Edit configuration
```
sudo nano /etc/fail2ban/jail.local
```
Add the following actions:
```
[ssh]
enabled = true
banaction = ufw-ssh
port = 2992
filter = sshd
logpath = /var/log/auth.log
maxretry = 3


[apache]
enabled = true
port = http,https
banaction = ufw-apache
filter = apache-auth
logpath = /var/log/apache*/error*.log
maxretry = 4


[apache-filenotfound]
enabled = true
port = http,https
banaction = ufw-apache
filter = apache-nohome
logpath = /var/log/apache*/error*.log
maxretry = 3


[apache-noscript]
enabled = true
port = http,https
banaction = ufw-apache
filter = apache-noscript
logpath = /var/log/apache*/error*.log
maxretry = 6


[apache-overflows]
enabled = true
port = http,https
banaction = ufw-apache
filter = apache-overflows
logpath = /var/log/apache*/error*.log
maxretry = 2
```
Create banaction files
```
sudo touch /etc/fail2ban/action.d/ufw-ssh.conf
sudo nano /etc/fail2ban/action.d/ufw-ssh.conf
```
Edit the file:
```
[Definition]
actionstart =
actionstop =
actioncheck =
actionban = ufw insert 1 deny from <ip> to any app OpenSSH
actionunban = ufw delete deny from <ip> to any app OpenSSH
```
Secondly:
```
sudo touch /etc/fail2ban/action.d/ufw-apache.conf
sudo nano /etc/fail2ban/action.d/ufw-apache.conf
```
Edit the file:
```
[Definition]
actionstart =
actionstop =
actioncheck =
actionban = ufw insert 2 deny from <ip> to any app "Apache Full"
actionunban = ufw delete deny from <ip> to any app "Apache Full"
```

https://blog.vigilcode.com/2011/05/ufw-with-fail2ban-quick-secure-setup-part-ii/


## Install logwatch

Logwatch can allow you to monitor the server's logs.
```
sudo apt-get install logwatch
sudo apt-get install mailutils
```

Full admission: I struggled a bit with logwatch and postfix. I finally configured logwatch to send to root, but I'm not sure I could repeat the configuration. The current configuration includes copying the debian configuration to main.cf.
```
sudo cp /usr/share/postfix/main.cf.debian /etc/postfix/main.cf
```
You also need to make sure there are proper aliases:
```
sudo newaliases
```
Start postfix.
```
sudo /etc/init.d/postfix start
```
To view yesterday's logs:
```
sudo logwatch
```
To view logs in root mail:
```
sudo mail
```


Reference: https://blog.vigilcode.com/2011/04/ubuntu-server-initial-security-quick-secure-setup-part-i/


## Manage Security Updates

```
sudo dpkg-reconfigure --priority=low unattended-upgrades
```
Answer yes to the question.

Reference: https://help.ubuntu.com/community/AutomaticSecurityUpdates


## Install Apapche

```
sudo apt-get install apache2
```
Say Yes to the question


## Install Mod-wsgi

```
sudo apt-get install libapache2-mod-wsgi
```

## Install postgresql

```
sudo apt-get install postgresql
```
Say yes to the questiosn.

Reference:
Installing LAPP
http://blog.udacity.com/2015/03/step-by-step-guide-install-lamp-linux-apache-mysql-python-ubuntu.html


## Install psycopg2

```
sudo apt-get install python-psycopg2
```

Reference: http://initd.org/psycopg/docs/install.html


## Testing Apache / Mod-wsgi

Best practice recommends configuring Apache to hand;e requests using the WSGI module. Details can found here:

https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4340119836/m-4815938843
https://www.udacity.com/course/viewer#!/c-ud299-nd/l-4340119836/m-4801869263


## Create PostgreSQL User 

```
sudo -i -u postgres
createuser --interactive
```
User 'catalog' was created initiall with CreasteDB permission. 

## Importing Database Elements from existing Heroku deployment 

I used a backup from my heroku deployment to import the structure of the database from my app there.

Reference: https://devcenter.heroku.com/articles/heroku-postgres-import-export


## PostgreSQL Remote Connections

Confirm that the default configuration does not allow remote connections by reviewing the configuration file.
```
sudo nano /etc/postgresql/9.3/main/pg_hba.conf 
```


## Limited permission for PostgreSQL user Catalog

After the database was imported, I created two roles:
catalog_crud, having select, update, insert and delete permissions to all tables;
catalog_connect, having connection permissions to the database.
Having created the needed tables, I altered the tables to be owned by catalog and I granted user catalog no createDB permissions. I also granted catalog_crud and catalog_connect to catalog.

Reference: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04


## Install git

```'
sudo apt-get install git
```

## Clone my repository

```
cd /var/www
sudo git clone https://github.com/qgreg/itemcatalog.git
```

Reference: https://help.github.com/articles/cloning-a-repository/


## Install required python packages

First install python pip
```
sudo apt-get install python-pip
```
Answer yes to the question
```
sudo pip install flask
sudo pip install WTForms
sudo pip install flask-wtf
sudo pip install flask-SQLAlchemy
sudo pip install oauth2client
```

## Create itemcatalog.wsgi

I adapted the existing runserver.py to create itemcatalog.wsgi. The path gets updated:
```
import sys
sys.path.insert(0, "/var/www/itemcatalog")
```
The createapp assignment gets changed from app to appplication. Edit the config path to the absolute path.

Reference: Configure a Flask app
http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/

## Configuring itemcatalog.conf

Create itemcatalog.conf and edit for the app.
```
sudo touch /etc/apache2/sites-enabled/itemcatalog.conf
sudo nano /etc/apache2/sites-enabled/itemcatalog.conf
```

References:
http://drumcoder.co.uk/blog/2010/nov/12/apache-environment-variables-and-mod_wsgi/
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps


## Securing  .git directory

Add the following line to itemcatalog.conf
```
RedirectMatch 404 /\.git
```

http://serverfault.com/questions/128069/how-do-i-prevent-apache-from-serving-the-git-directory


## Enable itemcatalog application
```
sudo a2ensite itemcatalog
```


## Get rid of the annoying sudo error
```
sudo nano /etc/hosts
```
If your machine name is ip-10-20-21-48, you append the name to the first line of the file:
```
127.0.0.1 localhost ip-10-20-21-48
```

Reference: http://askubuntu.com/questions/59458/error-message-when-i-run-sudo-unable-to-resolve-host-none


## Adapting app for deployment

Provide absolute paths to files
	config.py
	client_secrets.json
	fb_client_secrets.json
Provide correct databse URI
postgres://username:password@localhost/database


## Update Facebook and Google+ Logins

Update credentials for both providers with new urls.

Reference: Covered in Udacity course 


## Resolving AH0055 error

apache2: Could not determine the server's fully qualified domain name, 
using 127.0.0.1 for ServerName

Reference: http://askubuntu.com/questions/256013/could-not-reliably-determine-the-servers-fully-qualified-domain-name


## Automatic Updates

```
sudo apt-get install unattended-upgrades
```

Reference: https://help.ubuntu.com/lts/serverguide/automatic-updates.html

## Monitor Status

Install glances
''
sudo pip install Glances
```

To monitor application availability, start Glances from the command line:
```
glances
```

Reference: http://glances.readthedocs.org/en/latest/glances-doc.html#configuration
http://askubuntu.com/questions/293426/system-monitoring-tools-for-ubuntu
