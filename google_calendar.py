from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import pytz
import streamlit as st


class GoogleCalendar:

    def __init__(self, credentials, idcalendar):
        self.credentials = credentials
        self.idcalendar = idcalendar
        self.service = build('calendar', 'v3', credentials=service_account.Credentials.from_service_account_info(self.credentials, scopes=['https://www.googleapis.com/auth/calendar']))

    def create_event(self, name_event, start_time, end_time, timezone, attendees=None):
        event = {
            'summary': name_event,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        try:
            created_event = self.service.events().insert(calendarId=self.idcalendar, body=event).execute()
        except HttpError as error:
            raise Exception(f'An error occurred: {error}')
        
        return created_event
    
    def get_events(self, date=None):
        if not date:
            events = self.service.events().list(calendarId=self.idcalendar).execute()
        else:
            timezone = pytz.timezone("America/Argentina/Buenos_Aires")
            start_date = timezone.localize(datetime.strptime(date, '%Y-%m-%d')).isoformat()
            end_date = (timezone.localize(datetime.strptime(date, '%Y-%m-%d')) + timedelta(days=1)).isoformat()
            events = self.service.events().list(calendarId=self.idcalendar, timeMin=start_date, timeMax=end_date).execute()
        return events.get('items', [])

    def get_events_start_time(self, date):
        events = self.get_events(date)
        start_times = []

        for event in events:
            start_time = event['start'].get('dateTime')
            if start_time:
                parsed_start_time = datetime.fromisoformat(start_time[:-6])
                hours_minutes = parsed_start_time.strftime('%H:%M')
                start_times.append(hours_minutes)
        
        return start_times

# Función para convertir las fechas a la zona horaria deseada
def convert_to_timezone(naive_datetime_str, timezone_str):
    naive_datetime = datetime.strptime(naive_datetime_str, '%Y-%m-%dT%H:%M:%S')
    local_tz = pytz.timezone(timezone_str)
    local_datetime = local_tz.localize(naive_datetime)
    return local_datetime.isoformat()
