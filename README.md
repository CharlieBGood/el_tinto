# El Tinto

[![Build Status](https://travis-ci.org/charliebgood/piedpiper-web.svg?branch=master)](https://travis-ci.org/charliebgood/piedpiper-web)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

Daily newsletter for Colombian news. [documentation](http://charliebgood.github.io/piedpiper-web/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  

# Local Development

Start the dev server for local development:
```bash
docker-compose up
```

Run a command inside the docker container:

```bash
docker-compose run --rm web [command]
```
