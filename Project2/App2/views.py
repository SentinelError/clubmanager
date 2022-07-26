import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.shortcuts import render, HttpResponseRedirect
from .forms import NewUserForm, EventFormA, EventFormS, VenueForm, StudentForm, ReportForm, NewEditForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import Event, Venue, Report, Student


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        Sform = StudentForm(request.POST)

        if form.is_valid() and Sform.is_valid():
            user = form.save()

            student = Sform.save(commit=False)
            student.user = user

            student.save()

            # login(request, user)
            messages.success(request, "Registration successful.")
            return HttpResponseRedirect("/login")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    Sform = StudentForm()
    return render(request=request, template_name="App2/register.html",
                  context={"register_form": form, "Student": Sform})


def edit_request(request):
    if request.method == "POST":
        form = NewEditForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, ("Profile updated."))
            return HttpResponseRedirect("/clubhomepage")
    else:
        form = NewEditForm(instance=request.user)
    return render(request=request, template_name="App2/edituser.html", context={"edit_form": form, })


def changepassword(request):
    if request.method == "POST":
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, ("Registration successful."))
            return HttpResponseRedirect("/")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request=request, template_name="App2/passwordchange.html", context={"passwordchange_form": form, })


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/clubhomepage')
            else:
                messages.error(request, ("Invalid username or password."))
        else:
            messages.error(request, ("Invalid username or password."))
    form = AuthenticationForm()
    return render(request=request, template_name="App2/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.success(request, ("Logout successful."))
    return render(request=request, template_name='App2/homepage.html')


def homepage(request):
    return render(request=request, template_name='App2/homepage.html')


def clubhomepage(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    if request.user.is_authenticated:
        month = month.capitalize()
        monthnum = list(calendar.month_name).index(month)
        monthnum = int(monthnum)

        cal = HTMLCalendar().formatmonth(year, monthnum)

        now = datetime.now()
        cyear = now.year

        Identity = request.user.id
        events = Event.objects.filter(attendees=Identity,
                                      event_date__year=year,
                                      event_date__month = monthnum).order_by('event_date')
        return render(request, 'App2/clubhomepage.html',
                      {"events": events,
                       "year": year,
                       "month": month,
                       "monthnum": monthnum,
                       "cal": cal,
                       "cyear":cyear,})


    else:
        messages.error(request, ("You are not logged in."))
        return HttpResponseRedirect('/homepage')


def events(request):
    event1 = Event.objects.all().order_by('event_date')
    return render(request, 'App2/events.html', {'event1': event1})


def updevents(request, eventid):
    event = Event.objects.get(pk=eventid)
    if request.user == event.overseer or request.user.is_superuser:
        if request.user.is_superuser:
            form = EventFormA(request.POST or None, instance=event)
        else:
            form = EventFormS(request.POST or None, instance=event)

        if form.is_valid():
            form.save()
            messages.success(request, ("Event Updated."))
            return HttpResponseRedirect('/events')

    else:
        messages.error(request, ("Only the Admin or the Report Author can update the event."))
        return HttpResponseRedirect('/events')

    return render(request, 'App2/updateevents.html',
                  {'event': event,
                   'form': form})


def addevents(request):
    initial_data = {
        'name': 'Training'
    }
    if request.method == 'POST':
        if request.user.is_superuser:
            form = EventFormA(request.POST)
        else:
            form = EventFormS(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, ("Event Added."))
            return HttpResponseRedirect('/events')
    if request.user.is_superuser:
        form = EventFormA()
    else:
        form = EventFormS(initial=initial_data)
    return render(request=request, template_name='App2/addevent.html', context={'form': form, })


def delevents(request, eventid):
    event = Event.objects.get(pk=eventid)
    if request.user == event.overseer or request.user.is_superuser:
        event.delete()
        messages.success(request, ("Event Deleted."))
        return HttpResponseRedirect('/events')
    else:
        messages.error(request, ("Event deletion failed. Only Event Overseer or Admin can delete events."))
        return HttpResponseRedirect('/events')


def venues(request):
    venue1 = Venue.objects.all()
    return render(request, 'App2/venues.html', {'venue1': venue1})


def updvenues(request, venueid):
    venue = Venue.objects.get(pk=venueid)
    form = VenueForm(request.POST or None, instance=venue)

    if form.is_valid():
        form.save()
        messages.success(request, ("Venue Updated."))
        return HttpResponseRedirect('/venues')

    return render(request, 'App2/updatevenues.html',
                  {'venue': venue,
                   'form': form})


def delvenues(request, venueid):
    venue = Venue.objects.get(pk=venueid)
    if request.user.is_superuser:
        venue.delete()
        messages.success(request, ("Venue Deleted."))
        return HttpResponseRedirect('/venues')
    else:
        messages.error(request, ("Venue deletion failed. Only Admin can delete venues."))
        return HttpResponseRedirect('/venues')


def addvenues(request):
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ("Event Venue Added."))
            return HttpResponseRedirect('/venues')
    form = VenueForm()
    return render(request=request, template_name='App2/addvenue.html', context={'form': form, })


def reports(request):
    report1 = Report.objects.all()
    return render(request, 'App2/reports.html', {'report1': report1})


def addreport(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ("Report Added."))
            return HttpResponseRedirect('/reports')
    form = ReportForm()
    return render(request=request, template_name='App2/addreport.html', context={'form': form, })


def updreport(request, reportid):
    report = Report.objects.get(pk=reportid)
    if request.user == report.report_author or request.user.is_superuser:
        form = ReportForm(request.POST or None, instance=report)

        if form.is_valid():
            form.save()
            messages.success(request, ("Report updated."))
            return HttpResponseRedirect('/reports')

    else:
        messages.error(request, ("Only the Admin or the Report Author can update the report."))
        return HttpResponseRedirect('/reports')

    return render(request, 'App2/updatereport.html',
                  {'report': report,
                   'form': form})


def delreport(request, reportid):
    report = Report.objects.get(pk=reportid)
    if request.user == report.report_author or request.user.is_superuser:
        report.delete()
        messages.success(request, ("Report Deleted."))
        return HttpResponseRedirect('/reports')
    else:
        messages.error(request, ("Only the Admin or the Report Author can delete the report."))
        return HttpResponseRedirect('/reports')


def eventapproval(request):
    event2 = Event.objects.all()

    events_all = Event.objects.all()
    events_all_ids = []

    for i in range(0, len(events_all), 1):
        events_all_ids.append(str(events_all[i].id))

    if request.user.is_superuser:
        if request.method == "POST":
            id_list = request.POST.getlist('boxes')

            # update database

            for x in id_list:
                Event.objects.filter(pk=int(x)).update(approved=True)

            id_set_false = set(events_all_ids) - set(id_list)
            id_list_false = list(id_set_false)

            for y in id_list_false:
                Event.objects.filter(pk=int(y)).update(approved=False)

            messages.success(request, ("Event Approval Updated."))
            return HttpResponseRedirect('/eventapproval')
        else:
            return render(request=request, template_name='App2/eventapproval.html', context={"event2": event2})


    else:
        messages.error(request, ("You need to be an Admin to acces this page"))
        return HttpResponseRedirect('/events')


def users(request):
    user1 = User.objects.all().order_by('username')
    return render(request, 'App2/users.html', {'user1': user1})
