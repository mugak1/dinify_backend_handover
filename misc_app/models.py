from django.db import models


# Eod Status codes
# 0 = pending
# 1 = in progress

# restaurant level updates
# 2 = confirming daily orders
# 3 = new date set | new orders can come in
# 4 = organising records by EOD status
# 5 = reconciliations
# 6 = generating daily reports
# 7 = generating periodical reports e.g. weekly, monthly, etc
# 8 = sending notifications
# 9 = archiving records

# general eod status code
# 10 = completed
# 11 = failed
# 12 = cancelled


# Create your models here.
class SysActivityConfig(models.Model):
    id = models.AutoField(primary_key=True)
    config_name = models.CharField(max_length=255, unique=True, db_index=True)
    config_description = models.TextField(blank=True, null=True)
    config_type = models.CharField(max_length=50, choices=[
        ('boolean', 'Boolean'),
        ('integer', 'Integer'),
        ('string', 'String'),
        ('date', 'DateTime')
    ])
    config_boolean_value = models.BooleanField(default=False)
    config_integer_value = models.IntegerField(default=0)
    config_string_value = models.CharField(max_length=255, blank=True, null=True)
    config_date_value = models.DateField(null=True, blank=True)
    config_datetime_value = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sys_activity_config'
