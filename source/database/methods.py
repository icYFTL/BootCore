from . import Session
from .exceptions import NotActive
from .models import *
from .utils import *


class Methods:
    def __protected_active(func):
        def magic(self, *args, **kwargs):
            if self.user.status != 'active':
                raise NotActive()
            func(self, *args, **kwargs)

        return magic

    def __init__(self, **kwargs):
        self.__session = Session()
        if kwargs.get('user'):
            self.user = kwargs['user']
        else:
            self.user = self.get_user(**kwargs) if kwargs else None

    def add_user(self, user: User) -> None:
        self.__session.add(user)
        self.__session.commit()

    def is_email_exists(self, email: str) -> bool:
        return bool([x for x in self.__session.query(User).filter(User.email == email)])

    def is_service_exists(self, s_object: object) -> bool:
        if not is_service_object(s_object):
            raise TypeError('Not a service object')
        return bool([x for x in self.__session.query(s_object.__class__).filter(
            s_object.__class__.external_id == s_object.external_id)])

    def update_user(self, user: User) -> None:
        self.user = user
        self.__session.commit()

    def remove_user(self, user: User) -> None:
        self.__session.delete(user)
        self.__session.commit()

    def get_user(self, **kwargs) -> User:
        result = None

        if kwargs.get('vk'):
            result = [x for x in self.__session.query(service.VK).filter(service.VK.vk_id == kwargs['vk'])]
        elif kwargs.get('discord'):
            result = [x for x in
                      self.__session.query(service.Discord).filter(
                          service.Discord.discord_id == kwargs['discord'])]
        elif kwargs.get('twitch'):
            result = [x for x in
                      self.__session.query(service.Twitch).filter(service.Twitch.twitch_id == kwargs['twitch'])]
        elif kwargs.get('id'):
            result = [x for x in self.__session.query(User).filter(User.id == kwargs.get('id'))]
        elif kwargs.get('email'):
            result = [x for x in self.__session.query(User).filter(User.email == kwargs.get('email'))]

        if result:
            if issubclass(result[0].__class__, BaseServiceModel):
                return self.get_user(id=result[0].external_id)
            else:
                return result[0]

    @__protected_active
    def set_points(self, value: int, service=None) -> None:
        if value > 2 ** 30:
            value = 2 ** 30
        elif value < 0:
            value = 0

        delta = 0

        if self.user.points > value:
            delta = self.user.points - value
        else:
            delta = value - self.user.points

        self.user.points = value
        self.__session.add(Transaction(self.user.id, service, delta))

        self.__session.commit()

    @__protected_active
    def increase_points(self, value: int, service=None) -> None:
        value = abs(value)

        if self.user.points + value > 2 ** 30:
            self.user.points = 2 ** 30
        else:
            self.user.points += value

        self.__session.add(Transaction(self.user.id, service, value))
        self.__session.commit()

    @__protected_active
    def decrease_points(self, value: int, service=None) -> None:
        value = abs(value)
        if self.user.points - value < 0:
            self.user.points = 0
        else:
            self.user.points -= value
        self.__session.add(Transaction(self.user.id, service, -value))
        self.__session.commit()

    @__protected_active
    def integrate_service(self, s_object: object) -> None:
        if not is_service_object(s_object):
            raise TypeError('Not a service object')
        self.__session.add(s_object)
        self.__session.commit()

    @__protected_active
    def disintegrate_service(self, s_object: object) -> None:
        if not is_service_object(s_object):
            raise TypeError('Not a service object')

        self.__session.delete(s_object)
        self.__session.commit()
