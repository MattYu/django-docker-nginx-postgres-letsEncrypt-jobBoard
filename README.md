# ConcordiaAce

Job board made for Concordia University, Montreal, Canada, Co-op ACE program. 
# Features

| Security        | Job Ranking           | Media servicing  | User Notification  | Other Job Board Services  | Data  | CI/CD  |
| ------------- |:-------------:| :-----:|:-----:| :-----:|-----:|-----:|
| Google Captcha      | Candidate-Employer preference ranking system| Nginx file servicing | [django-notifications-hq](https://pypi.org/project/django-notifications-hq/) | Login as Admin, Candidate or Employer | Postgres Db| Prod Ready 2 step Docker-Compose setup
| Email activation|  ["hospital-resident" matching algorithm](https://pypi.org/project/matching/)      |   [Dynamic Plyr video player](https://github.com/sampotts/plyr)  | Email notification| Post jobs, interview invite, job matching | | Persistent Volumes
| Nginx-Sendfile Firewall |  |   Dynamic upload forms | | Apply to jobs
| uuid dynamic file paths |  |    Resume caching and reuse| | Search and filter jobs
| Email password reset |  | | | Search and filter candidates
| Let's Encrypt SSL | |  | | Full Admin Control (approval, permission assignment, etc.)
| | |  | | Google Map,  PDF Concatination
# Licensing
- All python/django code are created by us and available under MIT licence
- html template license was purchased for single app use for Concordia ACE website on http://preview.themeforest.net/item/oficiona-job-board-html-template/full_screen_preview/23042674 License must be re-purchased for other project. Permission to reuse template not under MIT license. 

# Dependencies

- Python 3.7
- Django 3.0
- django-file-resubmit==0.5.2
- django-sendfile==0.3.11
- django-sendfile2==0.5.1
- django-tinymce==2.8.0
- Pillow==6.2.1
- pytz==2019.3
- sqlparse==0.3.0
- six
- matching==1.1
- weasyprint
- requests
- psycopg2

- pypdf2


# Dev installation
1) Install git
2) Create a local directory, run:
   - Make a folder for the project
   - git init
   - git remote add upstream  https://github.com/MattYu/ConcordiaAce/.git
   - git fetch upstream
   - Create your own work branch: git checkout -b <name of your workbranch>
3) Install Python 3.7
   - When installing, on Windows, make sure to tick/select "pip", "install for all users" and "Add Python to environment variables"
   - Check that python has been successfully installed by running "python -v" in a console
   - Check that pip has been successfully installed by running "pip freeze" in a console
4) Strongly recommended: Install virtualenv
   - Run a powershell with admin privilege
   - Execute "Set-ExecutionPolicy Unrestricted"
   - Execute "pip install virtualenv"
5) Strongly recommended: Create a virtualenv for the project before installing dependancies 
   - go to project's folder
   - create a folder call cfehome
   - cd cfehome
   - create virtual env virtualenv .
   - run virtualenv ".\cfehome\Script\activate"
6) Install all dependencies, use same version as dependency section of readme
   - pip install django==3
   - pip install django-widget-tweaks
   - python -m pip install Pillow
   - pip install django-tinymce
   - pip install django-sendfile
   - pip install django-sendfile2
   - pip install django-file-resubmit
   - pip install six
   - pip install matching
   - pip install weasyprint
   - pip install requests
   - pip install psycopg2

  
7) Run server. Go to Ace folder.
  - python manage.py makemigrations
  - python manage.py migrate
  - python manage.py createsuperuser
      - User type = 4
  - python manage.py runserver

8) Push your branch. When ready to merge, make a pull request. Please never merge directly into master. 
  

# Commands

- > pip install virtualenv

-pip install django-widget-tweaks

-python -m pip install Pillow

-pip install django-tinymce

-pip install django-sendfile2

-pip install django-file-resubmit



Note that files upload will be service by Apache and x-file in production, on top of Django
