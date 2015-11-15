import json
from django.core.management.base import BaseCommand
# import time
from optparse import make_option
import logging
import sys

# # from background_task.tasks import tasks, autodiscover
from iconizer.iconizer_consts import ICONIZER_SERVICE_NAME
from iconizer.msg_service.msg_service_interface.msg_service_factory_interface import MsgServiceFactory
from obj_sys.models_ufs_obj import UfsObj


class Command(BaseCommand):
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

        factory = MsgServiceFactory()
        service = factory.get_msg_service()
        channel = service.create_channel("clipboard_to_django")
        # service.send_to("clipboard_monitor", {"msg_type": "register", "callback_msg_queue": channel.get_id()})
        # service.regsiter_to("clipboard_monitor", "clip_to_django")

        service.send_to(ICONIZER_SERVICE_NAME, {"command": "register_to_clipboard",
                                                "target": channel.get_channel_full_name()})
        while True:
            msg = channel.get_msg()
            if service.is_exit(msg):
                break
            demo_msg = {"msg_type": "clipboard", "data": msg}
            UfsObj.objects.get_or_create(description_json=json.dumps(demo_msg["data"]), ufs_obj_type=3)
        print "exiting handle function"

