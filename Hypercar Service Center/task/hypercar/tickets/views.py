from django.conf import settings
from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect


class WelcomeView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!<h2>')


class MenuView(View):
    menu = []
    template_name = 'menu.html'

    def get(self, request, *args, **kwargs):
        menu = [{'title': 'Change oil', 'link': 'change_oil'},
                {'title': 'Inflate tires', 'link': 'inflate_tires'},
                {'title': 'Get diagnostic test', 'link': 'diagnostic'}]
        return render(request, self.template_name, {'menu_items': menu})


class TicketView(View):
    template_name = 'ticket.html'

    def get(self, request, *args, **kwargs):
        path = request.path.split('/')[-1]  # last element of path
        estimate_minutes = 0
        work_time = {
            'change_oil': 2,
            'inflate_tires': 5,
            'diagnostic': 30
        }
        line_length = len(settings.CLIENTS)
        ticket_number = line_length + 1
        works = ()
        if line_length > 0:
            if path == 'change_oil':
                works = 'change_oil'
            if path == 'inflate_tires':
                works = ('change_oil', 'inflate_tires')
            if path == 'diagnostic':
                works = ('change_oil', 'inflate_tires', 'diagnostic')
            for client in settings.CLIENTS:
                if client['work'] in works:
                    estimate_minutes += work_time[client['work']]
        settings.CLIENTS.append({'work': path, 'ticket': ticket_number})
        context = {
            'ticket_number': ticket_number,
            'minutes_to_wait': estimate_minutes,
        }
        return render(request, self.template_name, context)


class ProcessingView(View):
    template_name = 'processing.html'

    def get(self, request, *args, **kwargs):
        change_oil = 0
        inflate_tires = 0
        diagnostic = 0
        for work in settings.CLIENTS:
            if work['work'] == 'change_oil':
                change_oil += 1
            if work['work'] == 'inflate_tires':
                inflate_tires += 1
            if work['work'] == 'diagnostic':
                diagnostic += 1
        clients = {'change_oil': change_oil,
                   'inflate_tires': inflate_tires,
                   'diagnostic': diagnostic}

        return render(request, self.template_name, {'clients': clients})

    def post(self, request, *args, **kwargs):
        ticket_next = 0
        if len(settings.CLIENTS):
            works = ('change_oil', 'inflate_tires', 'diagnostic')
            for work in works:
                for client in settings.CLIENTS:
                    if work == client['work']:
                        ticket_next = client['ticket']
                        settings.CLIENTS.remove(client)
                        break
                if ticket_next > 0:
                    break
        settings.TICKET = ticket_next
        return redirect('/next')


class NextView(View):
    template_name = 'next.html'

    def get(self, request):
        context = {'ticket': settings.TICKET}
        return render(request, self.template_name, context)
