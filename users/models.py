from django.db   import models

from core.models import TimeStampModel

class User(TimeStampModel):
    eamil        = models.CharField(max_length = 200, unique = True)
    password     = models.CharField(max_length = 200)
    name         = models.CharField(max_length = 20, null = True)
    phone_number = models.CharField(max_length = 20, null = True)
    address      = models.CharField(max_length = 200, null = True)
    point        = models.PositiveIntegerField(default = 1000000)

    class Meta:
        db_table = 'users'


