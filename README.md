# Concordia Co-op Ace Job Board
[![Website shields.io](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](http://aceconcordia.ca)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/) (Except Templates) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[https://concordia-ace.ca/](https://concordia-ace.ca/)

Job board made for Concordia University, Montreal, Canada, Co-op ACE program. 
# Features

| Security        | Job Ranking & Matching          | Media servicing  | User Notification  | Other Job Board Services  | Data  | CI/CD  |
| ------------- |:-------------:| :-----:|:-----:| :-----:|-----:|-----:|
| Google Captcha      | Candidate-Employer preference ranking system| Nginx file servicing | [django-notifications-hq](https://pypi.org/project/django-notifications-hq/) | ATS and full admin control | Postgres Db docker service| Prod Ready easy Docker-Compose setup and dedicated test docker-compose setup
| Email activation|  ["hospital-resident" matching algorithm](https://pypi.org/project/matching/)      |   [Dynamic Plyr video player](https://github.com/sampotts/plyr)  | Email notification| Post/review/edit jobs, interview invite, job matching, email notification | Persistent db mount | Persistent Volumes and storage mount, django migrations
| Nginx-Sendfile Firewall |  |   Dynamic upload forms | Annoncements | Apply to jobs/Cache old applications and autofill forms | | Separated test media and test db volumes with 99% coding sharing between prod and test docker-compose setups
| uuid protected dynamic file paths |  |    Secured resume caching and reuse| | E-commerce grade search and filter for jobs
| Email password reset |  | Sendfile + auth protected media| | Search and filter candidates 
| Let's Encrypt SSL with autorenewal | |  | | Login as Admin, Candidate or Employer
| | |  | | Google Map,  PDF Concatination
# Licensing
- All python/django code are created by us and available under MIT licence
- html template license was purchased for single app use for Concordia ACE website on http://preview.themeforest.net/item/oficiona-job-board-html-template/full_screen_preview/23042674 License must be re-purchased for other project. Permission to reuse template not under MIT license. 

# Launch code on your machine
For production
1) Make sure Docker is installed on the machine. No other installation is needed. 
2) Navigate to the root path of the files
3) Change env.dev keys to match production keys, including your host ip/domain name. 
4) Enter the following command `docker-compose -f production.yml up --build` 
5) If you are setting this up for the first time, or made changes to a db model. Create migration files and migrate the db tables: `docker exec -it <web id> python manage.py makegrations` and then `docker exec -it <web id> python manage.py migrate --no-input`. To find web id, `docker ps`.
6) The website is now running. You may access it using your host ip/domain name with any web browser
7) To create the first superuser (admin), run the command `docker exec -it yourWebDockerID python manage.py createsuperuser` . Choose user type 4 when asked. Subsequent admin can be created in the admin menu options.

For test

  Skip step 3) above. 

  4) Enter the following command `docker-compose up --build` 

  All other step are identical.
