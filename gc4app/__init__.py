# from celery import Celery
# import os
#
# def make_celery(appName=__name__):
#     redis_uri = os.getenv("BROKER_URL")
#     return Celery(appName,backend=redis_uri,broker=redis_uri)
#
# celery = make_celery()
