# piedpiper-web

[![Build Status](https://travis-ci.org/charliebgood/piedpiper-web.svg?branch=master)](https://travis-ci.org/charliebgood/piedpiper-web)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

Its all about a Weissman score > 5.0. Check out the project's [documentation](http://charliebgood.github.io/piedpiper-web/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)

# Initialize the project

Start the dev server for local development:

```bash
docker-compose up
```

Create a superuser to login to the admin:

```bash
docker-compose run --rm web ./management.py createsuperuser
```
