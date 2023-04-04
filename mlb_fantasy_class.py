import statsapi
import json
import os
from datetime import date

"""
MLB fantasy team builder created by Daniel Cazarez (2022)


To do: calculate fantasy score, optimize code/add filtering method,
work on DH position and make sure the same player cannot be added twice to a roster
"""


class MLBFantasyTeam:
    """Encapsulates all the methods belonging to the fantasy team builder"""

    # encode positions using 1-9 system
    __encode_positions = {
        1: 'P',
        2: 'C',
        3: '1B',
        4: '2B',
        5: '3B',
        6: 'SS',
        7: 'LF',
        8: 'CF',
        9: 'RF'
    }

    def __init__(self, filename: str) -> None:
        """Calls load_file() and creates new instance of fantasy team"""

        # creates folder for json file if DNE
        path = os.getcwd() + '/__jsondata__'
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        self.__fantasy_team = dict()
        self.__filename = '__jsondata__/' + filename
        self.__load_file(self.__filename)

    def __clear_screen(self) -> None:
        """Clears screen"""

        os.system('cls||clear')

    def start(self) -> None:
        """Starts the MLB fantasy CLI program"""

        while True:
            ans = input(
                f'\nPick an action (display roster, display stats, update roster, display fantasy score, delete team or enter q to exit): ')

            # sanitize input
            ans = ans.lower()

            print('\n')
            if ans == 'display roster':
                self.__clear_screen()
                self.__print_team()
            elif ans == 'display stats':
                self.__clear_screen()
                self.__display_stats()
            elif ans == 'update roster':
                self.__clear_screen()
                self.__update_roster()
            elif ans == 'delete team':
                self.__clear_screen()
                self.__delete_team()
                break
            elif ans == 'display fantasy score':
                print(
                    f'\nThe current fpts for your overall roster is: {self.__fetch_score()}\n')
            elif ans == 'q':
                self.__clear_screen()
                break
            else:
                print('Please choose one of the options\n')

    def __fetch_score(self) -> float:
        """
        Fetches fpts for each player in roster 
        based off ESPN scoring guideline for H2H fantasy baseball
        https://support.espn.com/hc/en-us/articles/360057163871-Standard-Scoring-for-Public-Baseball-leagues
        """

        print('\nFetching score...')
        print("\nScoring guidelines based on ESPN's head-to-head scoring guidelines for public leagues")
        print('\n More info: https://support.espn.com/hc/en-us/articles/360057163871-Standard-Scoring-for-Public-Baseball-leagues')

        fantasy_score = 0
        stats_dict = {}
        p_name = 'Pitcher: ' + self.__fantasy_team['P'][0]

        # append all hitting stats and pitching stats
        # to their respective lists
        for attributes in self.__fantasy_team.values():
            id = attributes[1]
            name = attributes[0]

            hitting_stats = statsapi.player_stat_data(
                id, group='[hitting]')['stats']
            pitching_stats = statsapi.player_stat_data(
                id, group='[pitching]')['stats']

            if pitching_stats:
                pitching_stats = pitching_stats[0]['stats']
                stats_dict['Pitcher: ' + name] = pitching_stats
            if hitting_stats:
                hitting_stats = hitting_stats[0]['stats']
                stats_dict['Hitter: ' + name] = hitting_stats

        for name, stats in stats_dict.items():
            if name == p_name:
                ip = float(stats['inningsPitched']) * 3
                hits_allow = -stats['hits']
                earned_runs = -stats['earnedRuns'] * 2
                walks_issued = -stats['intentionalWalks']
                Ks = stats['strikeOuts']
                wins = stats['wins'] * 5
                losses = -stats['losses'] * 5
                saves = stats['saves'] * 5

                p_score = round(ip + hits_allow + earned_runs +
                                walks_issued + Ks + wins + losses + saves, 2)
            else:
                r = stats['runs']
                tb = stats['totalBases']
                rbi = stats['rbi']
                walks = stats['intentionalWalks']
                Ks = -stats['strikeOuts']
                sb = stats['stolenBases']

                p_score = (r + tb + rbi + walks + Ks + sb)

            print(f'\n{name} fpts: {p_score}')
            fantasy_score += p_score

        return fantasy_score

    def __print_team(self) -> None:
        """Prints each player's position and attribute list"""

        print('Current fantasy team roster:\n')

        # print position and attribute list of each player in roster
        for position, attributes in self.__fantasy_team.items():
            print(f'Pos: {position}\nPlayer name and ID: {attributes}\n')

    def __display_stats(self) -> None:
        """Displays stats for each player in current fantasy team roster"""

        # display today's date before stats
        today_date = date.today().strftime("%m/%d/%y")
        print(f'FANTASY TEAM SEASON STATS AS OF {today_date}')

        # display player name alongside their season stats
        for attribute_list in self.__fantasy_team.values():
            print('======================================\n')
            player_name = attribute_list[0]
            print(f'Player name: {player_name}\n')
            print('Stats:')
            player_stats = statsapi.player_stats(attribute_list[1])
            print(player_stats)
            print('======================================')

            input("Press any key to continue paging")

    def __update_roster(self) -> None:
        """Allows user to update position on fantasy team based on 1-9 system"""

        print('\nChoose the position to update in your roster: ')
        for position in self.__fantasy_team.keys():
            print(position)

        while True:
            pos = input('\nPosition: ')

            # sanitize input
            pos = pos.upper()
            pos.strip()

            # if position is not found in current roster
            if pos not in self.__fantasy_team.keys():
                print('\nPlease enter a valid position')
            else:
                break

        if pos == 'P':
            print('\nTwo-way players can also play as pitchers.')

        while True:
            # check against position later when looping through results
            query_str = input(
                f'\nSearch for a {pos} player, or enter q to exit: ')

            if query_str.lower() == 'q':
                return

            search_res = statsapi.lookup_player(query_str)

            # filter out players who don't play
            # position we want, return a list of players who play as pos
            play_pos = self.__filter_players(search_res, pos)

            count = len(play_pos)

            print(f'\nSearch returned {count} players who play as {pos}\n')

            if count == 0:
                # handle a case of zero matching players who play that position
                print('\nPlease search again: ')
            else:
                break

        changes_made = False
        q_entered = False

        for player in play_pos:

            # exit if user has updated roster
            if changes_made or q_entered:
                break

            print(f"Player name: {player['fullName']}\n")
            print(f"Player ID: {player['id']}\n")

            while True:
                # selection
                ans = input(
                    'Would you like to add this player to your fantasy team? (Y/N) or enter q to exit: ')

                # sanitize input
                ans = ans.upper()

                if ans == 'Y':
                    player_name = player['fullName']
                    player_id = player['id']
                    self.__fantasy_team[pos] = [player_name, player_id]
                    changes_made = True
                    break
                elif ans == 'N':
                    break
                elif ans == 'Q':
                    q_entered = True
                    break
                else:
                    print('Please answer Y/N')

        if changes_made:
            print('\nChanges applied to fantasy roster.')
            print(f'New {pos}: {self.__fantasy_team[pos]}')

            with open(self.__filename, 'w') as f:
                json.dump(self.__fantasy_team, f)

            print('\nChanges saved.')
        else:
            print('\nNo roster changes applied.')

    def __filter_players(self, search_res: list, pos: str) -> list:
        """
        Filters players that don't match current position criteria,
        handles edge case of two-way players (which can play as pitchers)
        """

        play_pos = []
        for player in search_res:
            pos_abbr = player['primaryPosition']['abbreviation']
            if (pos_abbr == pos) or (pos_abbr == 'TWP' and pos == 'P'):
                play_pos.append(player)
        return play_pos

    def __delete_team(self) -> None:
        """Deletes current fantasy roster"""

        os.remove(self.__filename)
        print("Fantasy team deleted.\n")

    def __team_builder(self) -> None:
        """
        Builds the team dictionary which is of type dict[str]->list,
        adds each player according to 1-9 numbering system
        """

        player_cnt = 1

        print('\n')
        while (player_cnt <= 9):
            pos = self.__encode_positions[player_cnt]

            print(
                f'\nNow choosing position: {pos}')

            # lookups may be done using first, last, or full name of player
            query_str = input("\nInput a player's first, last, or fullname: ")

            # return dictionary of player data based off search query
            search_res = statsapi.lookup_player(query_str)

            # filters out players who do not match current pos,
            # handles special cases like TWP
            play_pos = self.__filter_players(search_res, pos)

            for player in play_pos:
                # fetch pos in case they're a TWP
                pos_abbr = player['primaryPosition']['abbreviation']

                print(pos_abbr, '\n')
                print('\n')
                print(f"Player name: {player['fullName']}\n")
                print(f"Player ID: {player['id']}\n")

                # selection
                ans = input(
                    'Would you like to add this player to your fantasy team? (Y/N): ')

                # sanitize input
                ans = ans.upper()

                if ans == 'Y':
                    # fetch full name of player and ID
                    player_name = player['fullName']
                    player_id = player['id']

                    # key = player position, value = [player name, player id]
                    self.__fantasy_team[pos] = [player_name, player_id]

                    # update player position to choose
                    player_cnt += 1
                    break
                elif ans == 'N':
                    # continue to next player if user chooses not to add current to roster
                    continue
                else:
                    # handle bad input, restart search
                    print('\n***Error: Please answer Y or N, restart lookup\n')
                    break

    def __create_team(self, filename: str) -> bool:
        """
        Invokes team_builder() if user answers Y, 
        returns None if user refuses to create new team
        """

        while True:
            ans = input(
                f'\n{filename} was not found, would you like to create a new team? (Y/N): ')

            # sanitize input
            ans = ans.upper()

            if ans == 'Y':
                # construct team and return dictionary of roster
                self.__team_builder()
                break
            elif ans == 'N':
                return False
            else:
                print('Please answer Y/N')

        return True

    def __load_file(self, filename: str) -> bool:
        """
        Checks if json containing fantasy team data exists, 
        invokes create_team() if it does not exist
        """

        try:
            with open(filename, 'r') as f:
                self.__fantasy_team = json.load(f)

                # json file already exists
                print('Fantasy team loaded successfully.\n')

        except FileNotFoundError:
            # create a team or allow
            # user to quit
            if self.__create_team(filename):
                # save contents of fantasy team
                with open(filename, 'w') as f:
                    json.dump(self.__fantasy_team, f)
                print('\nFantasy team created.')
            else:
                # user entered 'N'
                print('\nEnding script.')
                return False

        return True
