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
    GENDER_CHOICES = (
                        ('М', 'М'),
                        ('Ж', 'Ж'),
                     )

    YEAR_OF_BIRTH_CHOICES = ( 
                                ('1929', '1929'),
                                ('1930', '1930'),
                                ('1931', '1931'),
                                ('1932', '1932'),
                                ('1933', '1933'),
                                ('1934', '1934'),
                                ('1935', '1935'),
                                ('1936', '1936'),
                                ('1937', '1937'),
                                ('1938', '1938'),
                                ('1939', '1939'),
                                ('1940', '1940'),
                                ('1941', '1941'),
                                ('1942', '1942'),
                                ('1943', '1943'),
                                ('1944', '1944'),
                                ('1945', '1945'),
                                ('1946', '1946'),
                                ('1947', '1947'),
                                ('1948', '1948'),
                                ('1949', '1949'),
                                ('1950', '1950'),
                                ('1951', '1951'),
                                ('1952', '1952'),
                                ('1953', '1953'),
                                ('1954', '1954'),
                                ('1955', '1955'),
                                ('1956', '1956'),
                                ('1957', '1957'),
                                ('1958', '1958'),
                                ('1959', '1959'),
                                ('1960', '1960'),
                                ('1961', '1961'),
                                ('1962', '1962'),
                                ('1963', '1963'),
                                ('1964', '1964'),
                                ('1965', '1965'),
                                ('1966', '1966'),
                                ('1967', '1967'),
                                ('1968', '1968'),
                                ('1969', '1969'),
                                ('1970', '1970'),
                                ('1971', '1971'),
                                ('1972', '1972'),
                                ('1973', '1973'),
                                ('1974', '1974'),
                                ('1975', '1975'),
                                ('1976', '1976'),
                                ('1977', '1977'),
                                ('1978', '1978'),
                                ('1979', '1979'),
                                ('1980', '1980'),
                                ('1981', '1981'),
                                ('1982', '1982'),
                                ('1983', '1983'),
                                ('1984', '1984'),
                                ('1985', '1985'),
                                ('1986', '1986'),
                                ('1987', '1987'),
                                ('1988', '1988'),
                                ('1989', '1989'),
                                ('1990', '1990'),
                                ('1991', '1991'),
                                ('1992', '1992'),
                                ('1993', '1993'),
                                ('1994', '1994'),
                                ('1995', '1995'),
                                ('1996', '1996'),
                                ('1997', '1997'),
                                ('1998', '1998'),
                                ('1999', '1999'),
                                ('2000', '2000'),
                                ('2001', '2001'),
                                ('2002', '2002'),
                                ('2003', '2003'),
                                ('2004', '2004'),
                                ('2005', '2005'),
                                ('2006', '2006'),
                                ('2007', '2007'),
                                ('2008', '2008'),

                            )


    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_year = models.CharField(max_length=4, choices=YEAR_OF_BIRTH_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    reg_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

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
    team = models.ForeignKey('Team')
    representative = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()
    ip = models.GenericIPAddressField()
    date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.competition.name + ' ' + self.team.name  

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

    GENDER_CHOICES = (
                        ('М', 'М'),
                        ('Ж', 'Ж'),
                     )

    competition = models.ForeignKey('Competition')
    style = models.ForeignKey('Style')
    distance = models.ForeignKey('Distance')
    age = models.ForeignKey('Age')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    finished = models.BooleanField()

    
    def __str__(self):
        return self.competition.name + ' ' + self.style.name + ' ' + self.distance.name  + ' ' + self.age.name + ' ' + ('M' if self.gender else 'Ж')

#Участники
class Competitor(models.Model):
    """Competitor  model"""

    person = models.ForeignKey('Person')
    request = models.ForeignKey('Userrequest')
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
