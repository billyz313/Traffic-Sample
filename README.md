# Traffic-Sample

[![Python: 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IMapApps: Development](https://img.shields.io/badge/IMapApps-Development-green)](https://imapapps.com)

The purpose of this application is to demonstrate traffic flow data on a web application

## Setup and Installation
The installation described here will make use of conda to ensure there are no package conflicts with
existing or future applications on the machine.  It is highly recommended to use a dedicated environment
for this application to avoid any issues.

### Recommended
Conda (To manage packages within the application own environment)

### Clone Repo
```commandline
git clone git@github.com:billyz313/Traffic-Sample.git
```

### Environment
- Create the env

```commandline
conda env create -f environment.yml
```

- enter the environment

```shell
conda activate Traffic_sample
```

- Create database tables and superuser
###### follow prompts after each command
```shell
cd Traffic-Sample
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

At this point you should be able to start the application.  From the root directory you can run the following command

```shell
python manage.py runserver
```

### Contact

Please feel free to contact me if you have any questions.

### Authors

- [Billy Ashmall (NASA/USRA)](https://github.com/billyz313)
