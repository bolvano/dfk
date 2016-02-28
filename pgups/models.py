# -*- coding: utf-8 -*- 

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
    GENDER_CHOICES = ( ('М', 'М'),('Ж', 'Ж'), )

    YEAR_OF_BIRTH_CHOICES =  tuple( [tuple([str(x), str(x)]) for x in range(1929, 1998)] )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_year = models.CharField(max_length=4, choices=YEAR_OF_BIRTH_CHOICES, default=1997)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='Ж')
    reg_date = models.DateTimeField(auto_now=True)

    userrequest = models.ForeignKey('Userrequest')
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + self.birth_year + '/' + self.gender +')'


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
class Userrequest(models.Model):
    """Request  model"""
    competition = models.ForeignKey('Competition')
    team = models.ForeignKey('Team', null=True, blank=True)
    representative = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()
    ip = models.GenericIPAddressField()
    date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        team = '('+self.team.name+')' if self.team else '(Инд.)'
        return self.competition.name + ' ' + team  

    def get_client_ip(request):                                     
        # Получает IP пользователя
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


#Туры
class Tour(models.Model):
    """Tour  model"""

    GENDER_CHOICES = ( ('М', 'М'),('Ж', 'Ж'), )

    competition = models.ForeignKey('Competition')
    style = models.ForeignKey('Style')
    distance = models.ForeignKey('Distance')
    age = models.ForeignKey('Age')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    finished = models.BooleanField()
    
    def __str__(self):
        return self.style.name + ' ' + self.distance.name  + ' ' + self.age.name + ' ' + self.gender


#Участники
class Competitor(models.Model):
    """Competitor  model"""

    person = models.ForeignKey('Person')
    userrequest = models.ForeignKey('Userrequest')
    age = models.ForeignKey('Age')
    approved = models.BooleanField(default=False)
    tour = models.ForeignKey('Tour')
    prior_time = models.FloatField()
    main_distance = models.BooleanField()
    
    def __str__(self):
        if self.userrequest.team:
            team = self.userrequest.team.name
        else:
            team = 'Инд.'
        return self.person.last_name + ' ' + self.person.first_name + ' ('+ team +')' +': ' + self.tour.age.name + ' ' + self.tour.style.name + ' (' + str(self.prior_time) + ')'

# CDSG
class Cdsg(models.Model):
    competition = models.ForeignKey('Competition')
    name = models.CharField(max_length=255, null=True, blank=True, default='foo')
    number = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.name + ' #' + str(self.number)


#Старты
class Start(models.Model):
    """Start  model"""

    name = models.CharField(max_length=255, null=True, blank=True, default='foo')
    cdsg = models.ForeignKey('Cdsg')
    num = models.PositiveSmallIntegerField(default=1) # num in cdsg
    
    def __str__(self):
        return self.name + ' #' + str(self.num)

class Order(models.Model):
    """Start-Competitors bind model w/ lane position"""

    lane = models.PositiveIntegerField()
    start = models.ForeignKey('Start')
    competitor = models.ForeignKey('Competitor')   

    def __str__(self):
        return self.start.name + ' ' + self.competitor.person.last_name + ' (' + str(self.competitor.prior_time) + ')' + ' ' + str(self.lane)

    class Meta:
        ordering = ['lane']

#Результаты
class Result(models.Model):
    """Result  model"""

    competitor = models.ForeignKey('Competitor')
#    tour = models.ForeignKey('Tour')
#    start = models.ForeignKey('Start')
    time = models.DecimalField(max_digits=7, decimal_places=2)
    result = models.PositiveSmallIntegerField()
    points = models.PositiveSmallIntegerField()
    disqualification = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.competitor.__str__() + ' ' + self.competitor.tour.__str__() + ' ' + str(self.time)



'''
Пользователи
'''
