import traceback
import logging
from mlb_fantasy_class import MLBFantasyTeam

filename = 'mlbfantasy.json'
mlb_fantasy_team = MLBFantasyTeam(filename)
try:
    mlb_fantasy_team.start()
except Exception as e:
    print(f'\nException occured: {e}\n')
    logging.error(traceback.format_exc())
