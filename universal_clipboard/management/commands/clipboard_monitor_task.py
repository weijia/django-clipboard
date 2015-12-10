import json

# # from background_task.tasks import tasks, autodiscover
from django.contrib.auth.models import User

from cmd_handler_base.msg_process_cmd_base import MsgProcessCommandBase
from django_local_apps.server_configurations import get_admin_username
from iconizer.iconizer_consts import ICONIZER_SERVICE_NAME
from obj_sys.models_ufs_obj import UfsObj, Description


class ClipboardMsgHandler(MsgProcessCommandBase):
    def register_to_service(self):
        clipboard_receive_channel_name = "clipboard_to_django"
        channel = self.ufs_msg_service.create_channel(clipboard_receive_channel_name)
        self.ufs_msg_service.send_to(ICONIZER_SERVICE_NAME, {"command": "register_to_clipboard",
                                                             "target": channel.get_channel_full_name()})
        return channel

    # noinspection PyMethodMayBeStatic
    def process_msg(self, msg):
        clipboard_msg = {"msg_type": "clipboard", "data": msg}
        admin_username = get_admin_username()
        admin_user = User.objects.get(username=admin_username)
        description_content = unicode(msg["data"]["text"])
        description, is_description_created=Description.objects.get_or_create(content=description_content)
        obj, is_created = UfsObj.objects.get_or_create(description_json=json.dumps(clipboard_msg["data"]),
                                                       ufs_obj_type=UfsObj.TYPE_CLIPBOARD, user=admin_user,
                                                       ufs_url=u"clipboard://"+description_content)
        obj.descriptions.add(description)
        # obj.save()


Command = ClipboardMsgHandler
