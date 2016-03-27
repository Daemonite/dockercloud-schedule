## Daemonite Schedule

Docker Cloud PaaS scheduling service for staging cluster; Skunkworks.

- h/t https://github.com/alexdebrie/tutum-schedule
- h/t https://github.com/dbader/schedule

### Introduction

Designed to restrict the staging node cluster and its services to business hours only; 8am-8pm weekdays (Australian Eastern Standard).

### Usage

Schedule relies on the awesome Python [schedule](https://github.com/dbader/schedule) package created by `dbader`. It implements a simple, Pythonic interface to schedule tasks.

### Deploy

To deploy this to DockerCloud, create your own `dc-schedule.py` with your
desired configuration. Once you're ready, run:

    docker build -t <username>/<image_name> .
    docker push <username>/<image_name>

Go to your Docker Cloud account and deploy the Service. __Be sure to assign the
`global` role to the Service so it can use the Tutum API on your behalf.__

