import yaml
import signal
import threading
from application import Application
from datetime import date, datetime, timedelta

def load_config_file(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

app = Application()

config = load_config_file('config.yml')
start_date = datetime.strptime(config['start_date'], '%Y-%m-%d').date()
end_date = datetime.strptime(config['end_date'], '%Y-%m-%d').date()
app.start(config, start_date, end_date, config['opening_balance'])

