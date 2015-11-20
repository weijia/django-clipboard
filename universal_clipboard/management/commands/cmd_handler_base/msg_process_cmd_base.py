import logging
from optparse import make_option
from django.core.management import BaseCommand
import sys
from iconizer.msg_service.msg_service_interface.msg_service_factory_interface import MsgServiceFactory

__author__ = 'weijia'


class MsgProcessCommandBase(BaseCommand):

    def __init__(self):
        super(MsgProcessCommandBase, self).__init__()
        factory = MsgServiceFactory()
        self.ufs_msg_service = factory.get_msg_service()
        self.channel = None

    LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

    help = 'Run tasks that are scheduled to run on the queue'
    option_list = BaseCommand.option_list + (
        # make_option('--duration',
        #     action='store',
        #     dest='duration',
        #     type='int',
        #     default=0,
        #     help='Run task for this many seconds (0 or less to run forever) - default is 0'),
        # make_option('--sleep',
        #     action='store',
        #     dest='sleep',
        #     type='float',
        #     default=5.0,
        #     help='Sleep for this many seconds before checking for new tasks (if none were found) - default is 5'),
        make_option('--log-file',
                    action='store',
                    dest='log_file',
                    help='Log file destination'),
        make_option('--log-std',
                    action='store_true',
                    dest='log_std',
                    help='Redirect stdout and stderr to the logging system'),
        make_option('--log-level',
                    action='store',
                    type='choice',
                    choices=LOG_LEVELS,
                    dest='log_level',
                    help='Set logging level (%s)' % ', '.join(LOG_LEVELS)),
    )

    def _configure_logging(self, log_level, log_file, log_std):

        if log_level:
            log_level = getattr(logging, log_level)

        config = {}
        if log_level:
            config['level'] = log_level
        if log_file:
            config['filename'] = log_file

        if config:
            logging.basicConfig(**config)

        if log_std:
            class StdOutWrapper(object):
                def write(self, s):
                    logging.info(s)

            class StdErrWrapper(object):
                def write(self, s):
                    logging.error(s)

            sys.stdout = StdOutWrapper()
            sys.stderr = StdErrWrapper()

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.DEBUG)
        log_level = options.pop('log_level', None)
        log_file = options.pop('log_file', None)
        log_std = options.pop('log_std', False)
        # duration = options.pop('duration', 0)
        # sleep = options.pop('sleep', 5.0)

        # self._configure_logging(log_level, log_file, log_std)

        # autodiscover()
        #
        # start_time = time.time()
        #
        # while (duration <= 0) or (time.time() - start_time) <= duration:
        #     if not tasks.run_next_task():
        #         logging.debug('waiting for tasks')
        #         time.sleep(sleep)
        channel = self.register_to_service()
        while True:
            msg = channel.get_msg()
            if self.ufs_msg_service.is_exit(msg):
                break
            self.process_msg(msg)
        print "exiting handle function"

    def register_to_service(self):
        pass

    def get_channel(self, channel_name):
        if self.channel is None:
            self.channel = self.ufs_msg_service.create_channel(channel_name)
        return self.channel