#!/usr/bin/python
import datetime

import roman
import flask
from icalendar import Calendar, Event

import ps_data

app = flask.Flask(__name__)

@app.route('/')
def homepage():
    return flask.render_template('homepage.html', next_event=next_events().next())

@app.route('/next')
def next():
    return flask.render_template('next.html', events=next_events())

@app.route('/next.ics')
def nextics():
    return events_to_ical(next_events(), 'Upcoming Pub Standards Events')

@app.route('/all')
def all():
    return flask.render_template('all.html', events=all_events())

@app.route('/all.ics')
def allics():
    return events_to_ical(all_events(), 'All Pub Standards Events')

@app.route('/event/pub-standards-<numeral>')
def ps_event(numeral):
    try:
        number = roman.fromRoman(numeral.upper())
    except roman.InvalidRomanNumeralError:
        return "Invalid roman numeral!", 400
        
    event = ps_data.get_ps_event_by_number(number)
    return flask.render_template('event.html', event=event)

@app.route('/event/<slug>')
def other_event(slug):
    event = ps_data.get_ps_event_by_slug(slug)
    if not event:
        return "Unknown event", 404
    return flask.render_template('event.html', event=event)

@app.route('/keep-in-touch')
def keep_in_touch():
    return flask.render_template('keep-in-touch.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')


def next_events():
    now = datetime.datetime.now()
    future = now + datetime.timedelta(weeks=52)
    return ps_data.events(start=now, end=future)

def all_events():
    next_year = datetime.datetime.now() + datetime.timedelta(weeks=52)
    return ps_data.events(end=next_year)

def events_to_ical(events, title):
    cal = Calendar()
    cal.add('summary', title)
    cal.add('version', '2.0')
    for event in events:
        cal_event = Event()
        cal_event.add('uid', event.slug)
        cal_event.add('summary', event.title)
        cal_event.add('location', event.location + ", " + event.address)
        cal_event.add('dtstart', event.datetime['starts'])
        cal_event.add('dtend', event.datetime['ends'])
        cal.add_component(cal_event)

    return cal.to_ical(), 200, {'Content-Type': 'text/calendar'}

if __name__ == '__main__':
    app.run(debug=True)
