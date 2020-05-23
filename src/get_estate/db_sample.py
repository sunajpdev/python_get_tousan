from settings.db import session
from models.models import *

import pandas as pd

filename = 'data/processing/2020-05-07.csv'
df = pd.DataFrame(filename)
