from django.contrib import admin
from .models import  Competition, Team, Person, Age, Style, Distance, Userrequest, Tour, Competitor, Start, Cdsg, \
    TeamRelay, DistanceRelay, TourRelay, CompetitorRelay, StartRelay, CdsgRelay, Applicant

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

admin.site.register(Competition)
admin.site.register(Team)
admin.site.register(Person)
admin.site.register(Age)
admin.site.register(Style)
admin.site.register(Distance)
admin.site.register(Userrequest)
admin.site.register(Tour)
admin.site.register(Competitor)
admin.site.register(Start)
admin.site.register(Cdsg)

admin.site.register(TeamRelay)
admin.site.register(DistanceRelay)
admin.site.register(TourRelay)
admin.site.register(CompetitorRelay)
admin.site.register(StartRelay)
admin.site.register(CdsgRelay)



# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ApplicantInline(admin.StackedInline):
    model = Applicant
    can_delete = False
    verbose_name_plural = 'applicants'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ApplicantInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)



