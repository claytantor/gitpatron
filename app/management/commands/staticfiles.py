
import os
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--walkdir',
            action='store_true',
            dest='walkdir',
            default=False,
            help='Recurse through all subdirs'),
        )


    def handle(self, *args, **options):

        walkdir = args[0]

        for dirname, dirnames, filenames in os.walk('static'):
            # print path to all subdirectories first.
            for subdirname in dirnames:
                print os.path.join(dirname, subdirname)

            # print path to all filenames.
            for filename in filenames:
                print os.path.join(dirname, filename)

        # # Advanced usage:
        # # editing the 'dirnames' list will stop os.walk() from recursing into there.
        # if '.git' in dirnames:
        #     # don't go into any .git directories.
        #     dirnames.remove('.git')
