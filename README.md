# Concordia Co-op Ace Job Board
[![Website shields.io](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](http://aceconcordia.ca)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/) (Except Templates) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[https://concordia-ace.ca/](https://concordia-ace.ca/)

Job board made for Concordia University, Montreal, Canada, Co-op ACE program. 
# Features

| Security        | Job Ranking & Matching          | Media servicing  | User Notification  | Other Job Board Services  | Data  | CI/CD  |
| ------------- |:-------------:| :-----:|:-----:| :-----:|-----:|-----:|
| Google Captcha      | Candidate-Employer preference ranking system| Nginx file servicing | [django-notifications-hq](https://pypi.org/project/django-notifications-hq/) | ATS and full admin control | Postgres Db docker service| Prod Ready easy Docker-Compose setup and dedicated test docker-compose setup
| Email activation and confirmation |  ["hospital-resident" matching algorithm](https://pypi.org/project/matching/)      |   [Dynamic Plyr video player](https://github.com/sampotts/plyr)  | Email/Mass Email notification| Post/review/edit jobs, interview invite, job matching, email notification | Persistent db mount | Persistent Volumes and storage mount, django migrations
| Nginx-Sendfile Firewall |  |   Dynamic upload forms | Annoncements | Apply to jobs/Cache old applications and autofill forms | | Separated test media and test db volumes with 99% coding sharing between prod and test docker-compose setups
| uuid protected dynamic file paths |  |    Secured resume caching and reuse| | E-commerce grade search and filter for jobs
| Email password reset |  | Sendfile + auth protected media| | Search and filter candidates 
| Let's Encrypt SSL with autorenewal | |  | | Login as Admin, Candidate or Employer
| | |  | | Google Map,  PDF Concatination
# Licensing
- All python/django/yml code are created by us and available under MIT licence
- html template license was purchased for single app use for Concordia ACE website on [oficiona](https://themeforest.net/item/oficiona-job-board-html-template/23042674?gclid=CjwKCAjw8J32BRBCEiwApQEKgbP9mgS7W95LgCMymKU4waaAczkaKAq180Rv_QEZPPBjtvQkdnVa2BoCR-sQAvD_BwE) License must be re-purchased for other project. Permission to reuse template not under MIT license. 

# How to host the website on your Machine/Cloud Server
For production
1) Make sure [Docker](https://www.docker.com/) is installed and running on the machine. No other installation is needed. 
2) Clone this repo and navigate to its root path, where `production.yml` is located.
3) Make a `web.env`file (not included in the code) using the same format as `web.env.dev` file (include here) as template and in the same folder location. Change the keys to your own production keys:
    - Add your host ip/domain name to `DJANGO_ALLOWED_HOSTS`. (Note that your Domain Name must be linked to your server IP address. this is outside the scope of this readme; please consult your server provider for more details.)
    - Add your [Google reCaptcha V2](https://www.google.com/recaptcha/intro/v3.html) key (make sure that your domain is in your Google Key API account's allowed list) 
    - You should generate a new strong random `secret key`; this will be used for [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)).
    - Set `DEV=False`
    - Leave the DB login credentials idem (i.e. use the default linux postgre db login credentials) - the DB is not exposed to the web and there is no need to further secure it. 
    - Add your email credentials and `smtp` host. `web/ace/settings.py` uses PORT = 587 and TLS by default.
    - Add your [Google Map API key](https://cloud.google.com/maps-platform/) key (make sure that your domain is in the allowed list)
    - The `GOOGLE_API_KEY` is optional and currently not use, use the same key as dev to omit it.  

    - Make a `db.env` file with the same content as `db.env.dev`. 
    - In `production.yml`, add your domain to the letsEncryption environment parameters (i.e. replace concordia-ace.ca in `URL=concordia-ace.ca`with your own domain name). 
4) Enter the following command `docker-compose -f production.yml up --build` OR `docker-compose -f production.yml up --build -d` (deamon mode). This will spin up the docker server, install all dependencies and set up the website with https encryption.  
5) The website is now running. You may access it using your host `ip/domain name` with any web browser. Collection Static and migrations are automated in step 4), migration files are saved in your web/prod_storage/ directory. Db and media files are also stored in web/prod_storage folder via volume mount. Db Migration files are stored in web/appName/ `migration` subfolders.
6) To create the first superuser (admin), run the command `docker exec -it yourWebDockerID python manage.py createsuperuser` . Follow the on-screen instructions and choose user type `4` when asked. Subsequent admin can be created in the admin menu options. To find out the value of `yourWbDockerID`, run the command line `docker ps`

For test

  Skip step 2) above. 

  4) Enter the following command `docker-compose up --build`
  5) Go to `locahost` to access the website with any web browser. Media and db files are stored in virtual docker volumes not mounted to a physical location on the drive. 

  All other step are identical. Note: don't run test volumes on the same machine as prod volumes; they share the same volume names.

Turning on and off

- To turn off website: `docker-compose down`
- To turn on without rebuilding: `docker-compose -f production.yml up`
- To turn on with rebuilding: Step 4) above
