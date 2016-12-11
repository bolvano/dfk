# -*- coding: utf-8 -*- 

from django.db import models


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

    YEAR_OF_BIRTH_CHOICES =  tuple( [tuple([str(x), str(x)]) for x in range(1929, 2011)] )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_year = models.CharField(max_length=4, choices=YEAR_OF_BIRTH_CHOICES, default=2010)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='Ж')
    reg_date = models.DateTimeField(auto_now=True)

    userrequest = models.ForeignKey('Userrequest')
    
    def __str__(self):
        return self.last_name.title() + ' ' + self.first_name.title() + ' (' + str(self.birth_year) + '/' + \
               self.gender +')'


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

    def approved_competitors(self):
        return self.competitor_set.filter(approved=True)


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
    out = models.BooleanField(default=False)
    
    def __str__(self):
        out = ' (вне конкурса)' if self.out else ''
        return self.style.name + ' ' + self.distance.name  + ' ' + self.age.name + ' ' + self.gender + out


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

    time = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    result = models.PositiveSmallIntegerField(null=True)
    points = models.PositiveSmallIntegerField(null=True)
    disqualification = models.PositiveSmallIntegerField(default=0)

    lane = models.PositiveIntegerField(null=True)
    start = models.ForeignKey('Start', null=True)

    def __str__(self):
        if self.userrequest.team:
            team = self.userrequest.team.name
        else:
            team = 'Инд.'
        return self.person.last_name.title() + ' ' + self.person.first_name.title() + ' ('+ team +')' +': ' + \
               self.tour.age.name + ' ' + self.tour.style.name + ' (' + str(self.prior_time) + ')'

    class Meta:
        ordering = ['lane']

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

########################################
# Эстафеты #
########################################


# Дистанции
class DistanceRelay(models.Model):
    """Distance  model"""
    name = models.CharField(max_length=255)
    meters = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class TourRelay(models.Model):
    """TourRelay  model"""

    GENDER_CHOICES = (('М', 'М'), ('Ж', 'Ж'), ('С', 'С'))

    competition = models.ForeignKey('Competition')
    style = models.ForeignKey('Style')
    distance = models.ForeignKey('DistanceRelay')
    age = models.ForeignKey('Age')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    finished = models.BooleanField()
    out = models.BooleanField(default=False)

    def __str__(self):
        out = ' (вне конкурса)' if self.out else ''
        return self.style.name + ' ' + self.distance.name + ' ' + self.age.name + ' ' + self.gender + out


# CDSG
class CdsgRelay(models.Model):
    competition = models.ForeignKey('Competition')
    name = models.CharField(max_length=255, null=True, blank=True, default='foo')
    number = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.name + ' #' + str(self.number)


# Старты
class StartRelay(models.Model):
    """Start  model"""

    name = models.CharField(max_length=255, null=True, blank=True, default='foo')
    cdsg = models.ForeignKey('CdsgRelay')
    num = models.PositiveSmallIntegerField(default=1)  # num in cdsg

    def __str__(self):
        return self.name + ' #' + str(self.num)


#Участники
class TeamRelay(models.Model):

    """ ~ Competitor  model"""
    name = models.CharField(max_length=255, null=True, blank=True, default='foo')
    team = models.ForeignKey('Team')
    age = models.ForeignKey('Age')
    approved = models.BooleanField(default=False)
    tour = models.ForeignKey('TourRelay')

    time = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    result = models.PositiveSmallIntegerField(null=True)
    points = models.PositiveSmallIntegerField(null=True)
    disqualification = models.PositiveSmallIntegerField(default=0)
    lane = models.PositiveIntegerField(null=True)

    def __str__(self):
        if self.userrequest.team:
            team = self.userrequest.team.name
        else:
            team = 'Инд.'

        return team + ': ' + self.tour.age.name + ' ' + self.tour.style.name

    class Meta:
        ordering = ['lane']


class CompetitorRelay(models.Model):

    teamRelay = models.ForeignKey('TeamRelay')
    person = models.ForeignKey('Person')
    order = models.PositiveSmallIntegerField(default=1)  # order in relay
    start = models.ForeignKey('StartRelay', null=True)
    time = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    points = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        if self.teamRelay.userrequest.team:
            team = self.teamRelay.userrequest.team.name
        else:
            team = 'Инд.'
        return self.person.last_name.title() + ' ' + self.person.first_name.title() + ' ('+ team +')' +': ' + \
               self.teamRelay.tour.age.name + ' ' + self.teamRelay.tour.style.name