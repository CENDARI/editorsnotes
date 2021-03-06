## Installation
"SUPERSET" OF INSTRUCTIONS: 

UBUNTU:
----------------------------------------------------------------------------------
1. Check python version: (>2.7)
          python --version

2. Postgresql
   ```
   sudo apt-get install postgresql
   sudo apt-get install pgadmin3
   sudo -u postgres psql postgres
   sudo apt-get install postgresql-client
   sudo apt-get install postgresql-server-dev-9.3
   sudo -u postgres createdb mydb
   \password postgres
   ```
     +open pgAdmin gui & create new role & connect the db

3. Fabric
   ```
   sudo apt-get install python-pip python-dev build-essential
   sudo pip install fabric
   ```

4. libxml2 + libxslt
   ```
   sudo apt-get install libxml2
   sudo apt-get install libxml2-dev libxslt-dev
   ```

5. Elastic Search
   ```
   sudo apt-get install openjdk-7-jre
   wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.1.0.deb
   sudo dpkg -i elasticsearch-1.1.0.deb
   sudo service elasticsearch start
   ```

6. Nodejs
   ```
   sudo apt-get install -y python-software-properties python g++ make
   sudo add-apt-repository -y ppa:chris-lea/node.js
   sudo apt-get update
   sudo apt-get install nodejs
   ```

7. Less
   ```
   sudo apt-get install npm
   npm config set registry http://registry.npmjs.org
   sudo npm install -g less@1.3.3
   ```
   - you can use: `sudo apt-get install node-less` but this may not install the 1.3.3 version that we tested with 

10. Virtual Environment
    ```
    sudo pip install virtualenv
    ```

13.  Redis
     Install redis from http://redis.io/ for RQ (Redis Queue) to work.
     On ubuntu:
     ```
     apt-get install redis-server
     ```

14. Install flup
    ```
    sudo pip install flup
    ```

15. For pycurl install
    ```
    sudo apt-get install libcurl4-gnutls-dev
    ```

15. For odbc install
    ```
    sudo apt-get install unixodbc-dev
    ```

15. For Pillow/Image loading, install
    ```
    sudo apt-get install libjpeg-dev libtiff5-dev libopenjpeg-dev zlib1g-dev 
    ```

16. Inside Editors Notes Directory
    ```
    fab setup
    ```

    Create database in pgAdmin

    edit editorsnotes/settings_local.py with new database info

    ```
    sudo -u postgres fab sync_database
    ```

    Create a superuser and initial project
    ```
    fab create_superuser
    sudo service elasticsearch status
    ```
    (> check that elasticsearch is started)
    ```
    sudo fab runserver
    ```

17. Check the site:
    http://localhost:8000/

            
18.  ImageMagick
     Download from http://www.imagemagick.org/ version > 6.4

19.  iipsrv
     http://iipimage.sourceforge.net/
     Installation is a bit complicated. It needs apache2 and fastcgi.
     first install apache2, then mod_fastcgi, then the iipimage server
     On ubuntu:
     ```
     sudo apt-get install apache2-server libapache2-mod-fastcgi
     sudo apt-get install iipimage-server
     ```

     This will install `/etc/apache2/mods-available/iipsrc.conf` and
     a symbolic link to it from `/etc/apache2/mods-enabled`
     Add a filesystem prefix at this end of this file to limit the
     access of the server and facilitate communication with editorsnotes.
     Assuming your installation of editorsnotes is on a directory ENOTE,
     the images uploaded will be stored in ENOTE/uploads/scans/...
     Then, add the following line to `iipsrv.conf` (replace ENOTE with your dir):
     ```
     -initial-env MEMCACHED_SERVERS=localhost \
     -initial-env FILESYSTEM_PREFIX=ENOTE/uploads/
     ```

     or using the new syntax:
     ```
     FcgidInitialEnv MEMCACHED_SERVERS "localhost"
     FcgidInitialEnv FILESYSTEM_PREFIX "ENOTE/uploads/"
     ``` 

     To enable fastcgi module on apache2 for ubutu 14.04, you may have to do:
     ```
     sudo a2enmod fastcgi
     ```

     Sometimes this does not work due to access rights (all the directories
     on the path to ENOTE should be visible to iipsrv). In that case,
     create a directory /var/www/uploads and create a link to it in ENOTE.
     Beware of access rights ... (sudo mkdir ... and chown /var/www/uploads)
     Then, add /var/www/uploads/ to iipsrc.conf

20. Image conversion 
    When uploading images, an external process is used to do the
    conversion into a tiled pyramid file using the Imagemagick
    "convert" program.  The external process should run using the
    following program (can be in background):

    ```
    bin/python manage.py rqworker default
    ```

    This background program can be managed by the `supervisord`
    program if you have it installed. Look at the file
    `supervisor.conf` for an example on how t set it up.


21.    Watchdog (optional)
      ```
      sudo pip install watchdog
      ```

22.    VIPS
      ```
      sudo apt-get install libvips-tools
      ```
23.   Virtuoso
      The installation is too complex, based on virtuoso opensource 6.1

      ```
      sudo apt-get install libodbc1 odbcinst odbcinst1debian2 unixodbc-bin unixodbc-dev
      sudo apt-get install virtuoso-minimal virtuoso-opensource virtuoso-opensource-6.1-bin virtuoso-opensource-6.1-common virtuoso-server virtuoso-vad-conductor virtuoso-vad-isparql virtuoso-vad-ods virtuoso-vad-rdfmappers libvirtodbc0
      ```

      Following the documentation of virtuoso-python, create a file in `/etc/odbc.ini` containing the lines:
      ```
      [VOS]
      Description = Virtuoso
      Driver = /usr/lib/odbc/virtodbcu_r.so
      Servername = localhost
      Port = 1111
      UserName = dba 
      Locale = en.UTF-8
      ```

      That should work then with the default user dba.

MAC
Current realease doesnt work:
released used editorsnotes-0.6.0

Already had: python,python-dev, django, django-admin (?), pip 
+ brew install git

1. Install brew:
   ```
   ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"
   brew doctor
   ```

2. Install libxml2 
   ```
   brew install --with-python libxml2
   ```

3. Install libxslt
   ```
   brew install libxslt
   ```

4. Install ElasticSearch
   ```
   brew install ElasticSearch
   ```

5. Install Fabric
   ```
   sudo pip install fabric
   ```

5. Install Node.js
   Download from `http://nodejs.org/download/`
   `node-v0.10.21.pkg` in `/usr/local/bin`

6. Install LessCss: http://lesscss.org/
  ```
  sudo npm install -g less@1.3.3
  ```


7. Install Browserify
   ```
   sudo npm install browserify
   ```

8.  Install postgreSQL
    Download from http://www.enterprisedb.com/products-services-training/pgdownload#osx
    `postgresql-9.3.1-1-osx.dmg` (NOT?)

    ```
    brew install postgresql
    ```

9. Install watchdog (optional)
   ```
   brew install libyaml 
   sudo pip install watchdog
   ```
   (fab watch_static command to automatically collect and compile static files as they are changed.)

10. Install virtualenv
    ```
    sudo pip install virtualenv
    ```

11. Start Elastic Search
   ```
   sudo elasticsearch start
   ```

12. Install flup
    ```
    sudo pip install flup
    ```

13. Install bsddb3
    ```
    brew install berkeley-db --without-java
    sudo BERKELEYDB_DIR=/usr/local/Cellar/berkeley-db/5.3.28/ pip install bsddb3
    ```
    -  wjw - this manual installation technique is documented in more here http://chriszf.posthaven.com/getting-berkeleydb-working-with-python-on-osx)

14. Inside Editors Notes Directory
    ```
    fab setup
    ```

15. Database
    Create database in pgAdmin

    edit editorsnotes/settings_local.py with new database info

    ```
    fab sync_database
    fab runserver
    ```

16. Check the site:
   http://localhost:8000/

17. Image conversion 
    When uploading images, an external process is used to do the
    conversion into a tiled pyramid file using the Imagemagick
    "convert" program.  The external process should run using the
    following program (can be in background):

    ```
    bin/python manage.py rqworker default
    ```


