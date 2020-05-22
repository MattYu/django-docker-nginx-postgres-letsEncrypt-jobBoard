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
- All python/django code are created by us and available under MIT licence
- html template license was purchased for single app use for Concordia ACE website on http://preview.themeforest.net/item/Oficiona ACE-job-board-html-template/full_screen_preview/23042674 License must be re-purchased for other project. Permission to reuse template not under MIT license. 

# Launch code on your machine
For production
1) Make sure Docker is installed and running on the machine. No other installation is needed. 
2) Make a `web.env`file (not included in the code) using the same format as `web.env.dev` file (include here) as template and in the same folder location, but with your own production keys. Add your host ip/domain name to `DJANGO_ALLOWED_HOSTS`. Add your Google Captcha key (make sure that the key is linked to your domain) and Google Map API key and stmp email login credentials. The `GOOGLE_API_KEY` is optional and currently not use, use the same key as dev to omit it. You should generate a new strong `secret key`; this will be used for RSA. Leave the DB login credentials item (i.e. use the default linux postgre db login credentials) - the DB is not exposed to the web and there is no need to further secure it. Make a `db.env` file with the same content as `db.env.dev`. In `production.yml`, add your domain to the letsEncryption environment parameters (i.e. replace concordia-ace.ca in `URL=concordia-ace.ca`with your own domain name). 
3) Navigate to the root path of the files, where production.yml is located.
4) Enter the following command `docker-compose -f production.yml up --build` OR `docker-compose -f production.yml up --build -d` (deamon mode). This will spin up the docker server, install all dependencies and set up the website with https encryption.  
5) The website is now running. Collection Static and migrations are automated in step 4), migration files are saved in your web/prod_storage/ directory. You may access it using your host ip/domain name with any web browser. Db and media files are also stored in web/prod_storage folder via volume mount. 
6) To create the first superuser (admin), run the command `docker exec -it yourWebDockerID python manage.py createsuperuser` . Choose user type `4` when asked. Subsequent admin can be created in the admin menu options. To find out the value of `yourWbDockerID`, run the command line `docker ps`

For test

  Skip step 2) above. 

  4) Enter the following command `docker-compose up --build` 

  All other step are identical. Note: don't run test volumes on the same machine as prod volumes; they share the same volume names.

Turning on and off

- To turn off website: `docker-compose down`
- To turn on without rebuilding: `docker-compose -f production.yml up`
- To turn on with rebuilding: Step 4) above
