from django.db import models


# Model for 'common_numbers' table
class CommonNumbers(models.Model):
    word = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'common_numbers'


# Model for 'common_years' table
class CommonYears(models.Model):
    word = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'common_years'


# Model for 'high_probability_real_usernames' table
class HighProbabilityRealUsernames(models.Model):
    username = models.CharField(max_length=255, unique=True)
    search_result_title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    class Meta:
        db_table = 'high_probability_real_usernames'


# Model for 'high_rated_unames' table
class HighRatedUnames(models.Model):
    username = models.CharField(max_length=255)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'high_rated_unames'


# Model for 'high_rated_unames_history' table
class HighRatedUnamesHistory(models.Model):
    username = models.CharField(max_length=255)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'high_rated_unames_history'


# Model for 'names' table
class Names(models.Model):
    word = models.CharField(max_length=10)
    no_of_letters = models.IntegerField(db_column='NoOfLetters')

    class Meta:
        db_table = 'names'


# Model for 'words' table
class Words(models.Model):
    word = models.CharField(max_length=10)
    no_of_letters = models.IntegerField(db_column='NoOfLetters')

    class Meta:
        db_table = 'words'
