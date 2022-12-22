import os
import sys

from elasticsearch import Elasticsearch
from helpers import backoff

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings  # noqa


@backoff()
def wait_for_es():
    es_client = Elasticsearch(hosts=[test_settings.ELASTIC_DSN.hosts])
    if not es_client.ping():
        raise Exception


if __name__ == '__main__':
    wait_for_es()
