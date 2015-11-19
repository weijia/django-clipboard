import json

# # from background_task.tasks import tasks, autodiscover
from cmd_handler_base.msg_process_cmd_base import MsgProcessCommandBase
from iconizer.iconizer_consts import ICONIZER_SERVICE_NAME
from obj_sys.models_ufs_obj import UfsObj


class ClipboardMsgHandler(MsgProcessCommandBase):
    def register_to_service(self):
        clipboard_receive_channel_name = "clipboard_to_django"
        channel = self.service.create_channel(clipboard_receive_channel_name)
        self.service.send_to(ICONIZER_SERVICE_NAME, {"command": "register_to_clipboard",
                                                     "target": channel.get_channel_full_name()})
        return channel

    # noinspection PyMethodMayBeStatic
    def process_msg(self, msg):
        clipboard_msg = {"msg_type": "clipboard", "data": msg}
        UfsObj.objects.get_or_create(description_json=json.dumps(clipboard_msg["data"]), ufs_obj_type=3)


Command = ClipboardMsgHandler
