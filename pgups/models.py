from django.db import models

# Create your models here.

#Соревнования
class Competition(models.Model):
    """Competition model"""
    name = models.CharField(max_length=255)
    typ = models.CharField(max_length=255)
    date_start = models.DateField(db_index=True)
    date_end = models.DateField(db_index=True)
    finished = models.BooleanField()
    
    def __str__(self):
        return self.name

#Команды
class Team(models.Model):
    """Team model"""
    name = models.CharField(max_length=255)
    active = models.BooleanField()
    reg_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

#Люди
class Person(models.Model):
    """Person model"""
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_year = models.PositiveSmallIntegerField()
    gender = models.BooleanField() # true=male, false=female
    reg_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.fist_name + ' ' + self.last_name

#Возрастные группы
class Age(models.Model):
    """Age category model"""
    name = models.CharField(max_length=255)
    min_age = models.PositiveSmallIntegerField()
    max_age = models.PositiveSmallIntegerField()
    relay = models.BooleanField()
    kids = models.BooleanField()
    
    def __str__(self):
        return self.name

#Стили
class Style(models.Model):
    """Style  model"""
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

 #Дистанции
class Distance(models.Model):
    """Distance  model"""
    name = models.CharField(max_length=255)
    meters = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.name   

#Заявки
class Request(models.Model):
    """Request  model"""

    competition = models.ForeignKey('Competition')
    team = models.ForeignKey('Team')
    representative = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()
    ip = models.GenericIPAddressField()
    date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.competition.name + ' ' + self.team.name  

#Туры
class Tour(models.Model):
    """Tour  model"""

    competition = models.ForeignKey('Competition')
    style = models.ForeignKey('Style')
    distance = models.ForeignKey('Distance')
    age = models.ForeignKey('Age')
    gender = models.BooleanField() #true=male, false=female
    finished = models.BooleanField()

    
    def __str__(self):
        return self.competition.name + ' ' + self.style.name + ' ' + self.distance.name  + ' ' + self.age.name + ' ' + 'M' if self.gender else 'Ж'

#Участники
class Competitor(models.Model):
    """Competitor  model"""

    person = models.ForeignKey('Person')
    request = models.ForeignKey('Request')
    age = models.ForeignKey('Age')
    approved = models.BooleanField()

    tour = models.ForeignKey('Tour')
    
    def __str__(self):
        return self.person.last_name + ' ' + self.person.first_name  

#Старты
class Start(models.Model):
    """Start  model"""

    competitors = models.ManyToManyField('Competitor', related_name='in_starts', through='Order')
    
#    def __str__(self):
#        return self.name

class Order(models.Model):
    """Start-Competitors bind model w/ lane position"""

    lane = models.PositiveIntegerField()
    start = models.ForeignKey('Start')
    competitor = models.ForeignKey('Competitor')        

#Результаты
class Result(models.Model):
    """Result  model"""

    competitor = models.ForeignKey('Competitor')
    tour = models.ForeignKey('Tour')
#    start = models.ForeignKey('Start')
    time = models.DecimalField(max_digits=7, decimal_places=3)
    result = models.PositiveSmallIntegerField()
    points = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.competitor.__str__() + ' ' + self.tour.__str__()



'''
Пользователи
'''
