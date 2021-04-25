from vk_bot import VkGroup


# your own functions to use it in EventsHandler and SchedulerSettings class
class OwnFunctions(VkGroup):
    def send_date_to_me(self):
        message = "Проверка бота 7:30"
        self.send_message(to_id=315336001, message=message)


# Handle events that are offered and handle your own event(own_handler)
class EventsHandler(OwnFunctions):
    def if_new_message(self, message, from_id, event):
        pass
        # example
        if message == 'Привет':
            answer = 'Привет'
        else:
            answer = 'Пока'
        self.send_message(to_id=from_id, message=answer)

    def own_handler(self, event):  # own events handler https://vk.com/dev/groups_events
        pass


# add jobs to scheduler to do at intervals(GMT)
class SchedulerSettings(OwnFunctions):
    #  https://apscheduler.readthedocs.io/en/stable/modules/schedulers/background.html - self.scheduler
    def activate_scheduler(self):  # adding jobs
        pass
        self.scheduler.add_job(self.send_date_to_me, 'interval', days=1, start_date='2021-04-21 07:30:00')  # example


class ResultVKClientGroup(EventsHandler, SchedulerSettings):
    pass
