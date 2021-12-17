
from django.core.management.base import BaseCommand

from cs_api.models import CloudstackEventServer


class Command(BaseCommand):
    help = 'Listen for cloudstack events'

    def handle(self, *args, **kwargs):
        # TODO restart (or add the missing server somehow) when adding a new server
        servers = CloudstackEventServer.objects.all()
        print(f'found {len(servers)} server(s)')
        for server in servers:
            server.listen()
