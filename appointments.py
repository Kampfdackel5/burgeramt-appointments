from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import json
import logging
import time
import winsound


# With new Bürgeramt ID's as of 10.09.2022
ALL_BUERGERAMTS = (
    122208, 122210, 122217, 122219, 122226, 122227, 122231, 122238, 122243,
    122246, 122251, 122252, 122254, 122257, 122260, 122262, 122267, 122271,
    122273, 122274, 122276, 122277, 122279, 122280, 122281, 122282, 122283,
    122284, 122285, 122286, 122291, 122294, 122296, 122297, 122301, 122304,
    122309, 122311, 122312, 122314, 150230, 317869, 325657, 330436, 327262,
    327264, 327266, 327268, 327270, 327274, 327276, 327278, 327282, 327284,
    327286, 327290, 327292, 327298, 327300, 327312, 327314, 327316, 327318,
    327320, 327322, 327324, 327326, 327330, 327332, 327334, 327539, 327348,
    327352, 329742, 329745, 329748, 329751, 329760, 329763, 329766, 329772,
    329775
)

SERVICE_ID = 120686 #ID For Anmeldung
# Use 120335 for Abmeldung                <---- Untested (You can also do the Abmeldung by e-mail)
# Use 120703 for Personalausweis (ID)     <---- Untested
# Use 121151 for Pass (Passport)          <---- Untested

BEGIN_DATE = "2022-09-10"
END_DATE = "2021-10-30"

Beep_On_All = True   #With this set to "True" a sound is played, even when the date is not within the specified range.
Print_All = False     #With this set to "True" all available dates will be printed to the console, even when the date is not within the specified range.

# Without a user agent, you will get a 403
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
}

def get_appointment_dates(buergeramt_ids=ALL_BUERGERAMTS, service_id=SERVICE_ID):
    """
    Retrieves a list of appointment dates from the Berlin.de website.
    :param buergeramt_ids: A list of IDs of burgeramts to check
    :service_id: The service ID of the desired service. This is a URL parameter - the service ID has no meaning.
    :returns: A list of date objects
    """
    buergeramt_ids = [str(bid) for bid in buergeramt_ids]
    params = {
        'termin': 1,  # Not sure if necessary
        'dienstleisterlist': ','.join(buergeramt_ids),
        'anliegen[]': service_id,
    }
    response = requests.get('https://service.berlin.de/terminvereinbarung/termin/tag.php', params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    month_widgets = soup.find_all(class_='calendar-month-table')
    today = datetime.now().date()

    # Current month and next month
    # I will not expand this, because I would have to work with timestamps and I want to keep my sanity. Many dates this far away often have appointments available anyways.
    available_dates = []
    for index, month_widget in enumerate(month_widgets):
        # Get a list of available dates for each calendar widget. The first widget shows the current month.
        displayed_month = (today.month + index) % 12
        available_day_links = month_widget.find_all('td', class_='buchbar')
        available_days = [int(link.find('a').text) for link in available_day_links]
        available_dates += [today.replace(month=displayed_month, day=available_day) for available_day in available_days]

    if Beep_On_All==True and len(available_dates) > 0:
        frequency = 2500  # Set Frequency To 2500 Hertz
        duration = 1000  # Set Duration To 1000 ms == 5 second
        winsound.Beep(frequency, duration)
    
    if Print_All==True and len(available_dates) > 0:
        string_available_dates = ','.join(available_dates)
        print("Available dates: " + string_available_dates)
    else:
        print("No available dates found. Continuing search...")

    return available_dates


def appointment_dates(dates):
    dates = [d.strftime('%Y-%m-%dT%H:%M:%S') for d in dates]
    
    if len(dates) > 0:
        string_dates = ','.join(dates)
        print("Appointment found: " + string_dates) #Prints the appointment dates fitting the specification to the console.
    else:
        print("No appointments found. Continuing search...")


def observe(limit, polling_delay):
    """
    Polls for available appointments every [polling_delay] seconds for [limit] minutes/hours/days.
    :param limit: A timedelta. The observer will stop after this amount of time is elapsed
    :param polling_delay: The polling delay, in seconds.
    """
    start = datetime.now()
    duration = timedelta()
    while duration < limit:
        duration = datetime.now() - start
        appointment_dates(get_appointment_dates())
        time.sleep(polling_delay)


if __name__ == "__main__":
    observe(timedelta(days=30), polling_delay=30)
