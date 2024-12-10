from django.db import models
from django.utils.timezone import now

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Vocabulary(models.Model):
    german = models.CharField(max_length=100)
    english = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="vocabularies")
    rating = models.IntegerField(default=0)  # Bewertung von 0 bis 5

    def __str__(self):
        return f"{self.german} - {self.english} ({self.category.name}) - Bewertung: {self.rating}"

class TestResult(models.Model):
    date = models.DateTimeField(default=now)  # Zeitstempel des Tests
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    total_questions = models.IntegerField(default=10)  # Anzahl der Fragen
    correct_answers = models.IntegerField(default=0)  # Anzahl der richtigen Antworten
    wrong_answers = models.IntegerField(default=0)  # Anzahl der falschen Antworten

    def __str__(self):
        return f"Test am {self.date.strftime('%d.%m.%Y %H:%M:%S')} - Kategorie: {self.category.name if self.category else 'Alle'}"

class VocabularyTestResult(models.Model):
    test = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name="vocab_results")
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)
    correct = models.BooleanField()

    def __str__(self):
        return f"{self.vocabulary.german} - {'Richtig' if self.correct else 'Falsch'}"