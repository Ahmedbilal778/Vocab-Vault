from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

INTERVALS = [1, 3, 7, 14, 30]  # days per box: wrong->1, correct->3, twice->7 ...

class Word(models.Model):
    DIFF = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    meaning = models.CharField(max_length=255)
    example = models.TextField(blank=True)
    synonyms = models.CharField(max_length=255, blank=True)
    antonyms = models.CharField(max_length=255, blank=True)
    part_of_speech = models.CharField(max_length=50, blank=True)
    pronunciation = models.CharField(max_length=100, blank=True)
    hindi_meaning = models.CharField(max_length=255, blank=True)
    own_example = models.TextField(blank=True)
    date_learned = models.DateField(default=timezone.localdate)
    difficulty = models.CharField(max_length=10, choices=DIFF, default="medium")
    box = models.IntegerField(default=0)
    next_review = models.DateField(default=timezone.localdate)
    correct = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date_learned", "-id"]

    @property
    def status(self):
        if self.correct + self.wrong == 0: return "New"
        if self.box >= 3: return "Mastered"
        return "In Practice"

    @property
    def is_weak(self):
        return self.wrong > self.correct

    def record(self, ok):
        if ok:
            self.correct += 1; self.box = min(self.box + 1, 4)
        else:
            self.wrong += 1; self.box = 0
        self.next_review = timezone.localdate() + timedelta(days=INTERVALS[self.box])
        self.save()
        PracticeLog.objects.create(user=self.user, word=self, correct=ok)

    def __str__(self): return self.word

class PracticeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    correct = models.BooleanField()
    date = models.DateField(default=timezone.localdate)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    daily_goal = models.PositiveIntegerField(default=10)
