# from django.apps import AppConfig
# from django.db.models.signals import post_migrate
# from django.contrib.auth.models import Group


# def create_default_groups(sender, **kwargs):
#     for group_name in ['admin', 'secretary', 'director']:
#         Group.objects.get_or_create(name=group_name)


# class CoreConfig(AppConfig):
#     name = 'core'

#     def ready(self):
#         post_migrate.connect(create_default_groups, sender=self)


from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    
    for group_name in ['admin', 'secretary', 'director']:
        Group.objects.get_or_create(name=group_name)

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)
