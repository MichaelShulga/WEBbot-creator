import vk_api
from vk_api.bot_longpoll import VkBotEventType
from vk_bot import VkGroup  # hidden module

""" 
Available Methods
send_message(self, to_id, message)
wall_post(self, message)
"""


# your own functions to use it in EventsHandler and SchedulerSettings classes
class OwnFunctions(VkGroup):
    def send_check(self):
        message = "Проверка бота"
        self.send_message(to_id=315336001, message=message)


# Handle events that are offered and handle your own event(own_handler)
class EventsHandler(OwnFunctions):
    def message_new(self, message, from_id, event):  # new message
        if message == 'Привет':
            answer = 'Привет'
        elif message == 'Сделай пост':
            self.wall_post(message="Test")
            answer = 'Сделано'
        else:
            answer = 'Пока'
        self.send_message(to_id=from_id, message=answer)

    def message_typing_state(self, from_id, event):  # someone typing text
        message = 'You are typing some text'
        self.send_message(to_id=from_id, message=message)

    def group_join(self, from_id, event):  # new user joined(subscriber)
        message = 'New subscriber'
        self.send_message(to_id=from_id, message=message)

    def group_leave(self, from_id, event):  # user left group
        message = 'Why did you unsubscribe?'
        self.send_message(to_id=from_id, message=message)

    def own_handler(self, event):  # your own event handler https://vk.com/dev/groups_events
        # # example message_new event handler
        # if event.type == VkBotEventType.MESSAGE_NEW:
        #     self.message_new(message=event.obj.message['text'],
        #                      from_id=event.obj.message['from_id'],
        #                      event=event)
        pass


# add jobs to scheduler to do at intervals(GMT)
class SchedulerSettings(OwnFunctions):
    def activate_scheduler(self):  # https://apscheduler.readthedocs.io/en/stable/modules/schedulers/background.html
        # example
        self.scheduler.add_job(self.send_check, 'interval', days=1, start_date='2021-04-21 07:30:00')


# Do not need to change
class ResultVKClientGroup(EventsHandler, SchedulerSettings):
    pass
