from django.db import models

from editorsnotes.main.models import Topic

class PlaceTopicModel(models.Model):
    topic = models.OneToOneField(Topic, related_name='location')
    lon = models.FloatField()
    lat = models.FloatField()

    @property
    def latlong(self):
        return [self.lat, self.lon]
