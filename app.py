import streamlit as st
from streamlit_option_menu import option_menu
from send_email import send
from google_sheets import GoogleSheets
import re
import uuid
from google_calendar import GoogleCalendar
import numpy as np
import datetime as dt
import pytz

##VARIABLES
page_title = "Club de Padel"
page_icon = "🥎"
layout = "centered"

horas = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
pistas = ["Pista 1", "Pista 2"]

document = "gestion-club-padel"
sheet = "reservas"
credentials = st.secrets["google"]["credentials_google"]
idcalendar = "aaparicio1422@gmail.com"
idcalendar2 = "6b68dba35cf4ea9835366e1633bb9aa02d29354bbfd4b373d41b0bae26c94e4a@group.calendar.google.com"
time_zone = "America/Argentina/Buenos_Aires"

#FUNCIONES
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
    
def generate_uid():
    return str(uuid.uuid4())

def add_hour(time):
    parsed_time = dt.datetime.strptime(time, "%H:%M").time()
    #new_time = parsed_time + dt.timedelta(hours=1)
    new_time = (dt.datetime.combine(dt.date.today(),parsed_time) + dt.timedelta(hours=1, minutes=00)).time()
    return new_time.strftime("%H:%M")

def convert_to_timezone(naive_datetime_str, timezone_str):
    naive_datetime = dt.datetime.strptime(naive_datetime_str, '%Y-%m-%dT%H:%M:%S')
    local_tz = pytz.timezone(timezone_str)
    local_datetime = local_tz.localize(naive_datetime)
    return local_datetime.isoformat()

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

st.image("assets/image_main3.jpg")
st.title("Club de Padel")
st.text("Calle Alvear Nº346")

selected = option_menu(menu_title=None, options=["Reservar", "Pistas", "Detalles"], icons=["calendar-date", "building", "clipboard-minus"], orientation="horizontal")

if selected == "Detalles":
    st.subheader("Ubicacion")
    st.markdown('<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d13131.221174732313!2d-58.40592325!3d-34.634360349999994!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses!2sar!4v1716299824403!5m2!1ses!2sar" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>', unsafe_allow_html=True)

    st.header("Horarios")
    dia, hora = st.columns(2)

    dias_horas = [("Lunes", "10:00 - 19:00"), ("Martes", "10:00 - 19:00"), ("Miércoles", "10:00 - 19:00"), 
                  ("Jueves", "10:00 - 19:00"), ("Viernes", "10:00 - 19:00"), ("Sábado", "10:00 - 19:00"), 
                  ("Domingo", "10:00 - 19:00")]

    for d, h in dias_horas:
        dia.text(d)
        hora.text(h)
    
    st.subheader("Contacto")
    st.text("📞+541136739863")

    st.subheader("Instagram")
    st.markdown("Síguenos [aquí](https://www.instagram.com/laspalmaspadel/?hl=es) en Instagram")

if selected == "Pistas":
    st.image("assets/pista_1.jpg", caption="Esta es una de nuestras pistas")
    st.image("assets/pista_2.jpg", caption="Esta es una de nuestras pistas")

if selected == "Reservar":
    st.subheader("Reservar")
    
    c1, c2 = st.columns(2)

    nombre = c1.text_input("Tu nombre", placeholder="Nombre", label_visibility="hidden")
    email = c2.text_input("Tu email")
    fecha = c1.date_input("Fecha")
    pista = c1.selectbox("Pista", pistas)
    
    if fecha:
        if pista == "Pista 1":
            id = idcalendar
        elif pista == "Pista 2":
            id = idcalendar2
        calendar = GoogleCalendar(credentials, id)
        hours_blocked = calendar.get_events_start_time(str(fecha))
        result_hours = np.setdiff1d(horas, hours_blocked)
    hora = c2.selectbox("Hora", result_hours)
    
    notas = c2.text_area("Notas")

    enviar = st.button("Reservar")

    ##BACKEND

    if enviar:
        if nombre == "":
            st.warning("El nombre es obligatorio")
        elif email == "":
            st.warning("El email es obligatorio")
        elif not validate_email(email):
            st.warning("El email no es válido")
        else:
            # Crear evento en Google Calendar
            start_time_naive = dt.datetime.combine(fecha, dt.datetime.strptime(hora, "%H:%M").time())
            end_time_naive = start_time_naive + dt.timedelta(hours=1)

            start_time = start_time_naive.strftime('%Y-%m-%dT%H:%M:%S')
            end_time = end_time_naive.strftime('%Y-%m-%dT%H:%M:%S')

            start_time = convert_to_timezone(start_time, time_zone)
            end_time = convert_to_timezone(end_time, time_zone)

            calendar = GoogleCalendar(credentials, id)
            calendar.create_event(nombre, start_time, end_time, time_zone)
            
            # Crear registro en Google Sheets
            uid = generate_uid()
            data = [[nombre, email, pista, str(fecha), hora, notas, uid]]
            gs = GoogleSheets(credentials, document, sheet)
            range = gs.get_last_row_range()
            gs.write_data(range, data)

            # Enviar email al usuario
            send(email, nombre, fecha, hora, pista)

            st.success("Su pista ha sido reservada de forma exitosa.")

