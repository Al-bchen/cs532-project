# import things
import flask
from flask import request, jsonify, render_template, redirect
from flask_table import Table, Col

from mongodb_project_package import *

# connect MongoDB as client
client = MongoClient('localhost', 27017)

# use database
db = client['project']

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def index():
    heroes = get_all_heroes(db)
    leagues = get_all_leagues(db)

    class ItemTableHero(Table):
        hero_id = Col('hero ID')
        localized_name = Col('name')

    table_heroes = ItemTableHero(heroes)
    table_heroes.table_id = 'table_heroes'
    table_heroes.classes = ['display']

    class ItemTableLeague(Table):
        order = Col('order')
        leagueid = Col('league ID')
        name = Col('name')
        winner = Col('winner')

    table_leagues = ItemTableLeague(leagues)
    table_leagues.table_id = 'table_leagues'
    table_leagues.classes = ['display']

    return render_template('template_index.html', table_heroes=table_heroes, table_leagues=table_leagues)


@app.route('/leagues', methods=['GET'])
def leagues():
    all_league_stats = query_all_leagues_stats(db)

    # transform all_league_stats
    for d in all_league_stats:
        d['avg_duration'] = f"{d['avg_duration']:.2f} mins"
        d['radiant_win_rate'] = f"{d['radiant_win_rate'] * 100:.2f}%"
        d['dire_win_rate'] = f"{d['dire_win_rate'] * 100:.2f}%"

    # display league stats
    class ItemTableLeagueStats(Table):
        order = Col('order')
        leagueid = Col('league ID')
        name = Col('league name')
        winner = Col('winner')
        count = Col('match count')
        avg_duration = Col('Average game duration')
        radiant_win_rate = Col('radiant w%')
        dire_win_rate = Col('dire w%')
        radiant_win_count = Col('radiant wins')
        dire_win_count = Col('dire wins')

    table_all_league_stats = ItemTableLeagueStats(all_league_stats)
    table_all_league_stats.table_id = 'table_all_league_stats'
    table_all_league_stats.classes = ['display']

    return render_template('template_all_league_stats.html', table_all_league_stats=table_all_league_stats)


@app.route('/league/<int:leagueid>', methods=['GET'])
def league_base(leagueid: int):
    return redirect(f"/league/{leagueid}/hero_stats")


@app.route('/league/<int:leagueid>/hero_stats', methods=['GET'])
def league_hero_stats(leagueid: int):
    league_info = query_league_by_id(db, leagueid)
    hero_stats = query_one_league_hero_stats(db, leagueid)
    hero_not_active = query_one_league_all_hero_inactive(db, leagueid)
    for d in hero_stats:
        d.update({'winrate': f"{d['winrate'] * 100:.2f}%", 'winrate_bans': f"{d['winrate_bans'] * 100:.2f}%"})

    class ItemTableHeroStats(Table):
        hero_id = Col('hero ID')
        name = Col('hero name')
        contests = Col('picks + bans')
        picks = Col('picks')
        winrate = Col('winrate')
        bans = Col('bans')
        winrate_bans = Col('w% of bans')
        wins = Col('wins')
        losses = Col('losses')
        wins_of_bans = Col('wins of bans')

    table_hero_stats = ItemTableHeroStats(hero_stats)
    table_hero_stats.table_id = 'table_hero_stats'
    table_hero_stats.classes = ['display']

    class ItemTableHeroNotActive(Table):
        hero_id = Col('hero ID')
        name = Col('hero name')

    table_hero_not_active = ItemTableHeroNotActive(hero_not_active)
    table_hero_not_active.table_id = 'table_hero_not_active'
    table_hero_not_active.classes = ['display']

    return render_template("template_league_hero_stats.html", league_info=league_info, table_hero_stats=table_hero_stats,
                           table_hero_not_active=table_hero_not_active)


@app.route('/league/<int:leagueid>/league_stats', methods=['GET'])
def league_league_stats(leagueid: int):
    league_info = query_league_by_id(db, leagueid)
    league_stats = query_one_league_league_stats(db, leagueid)
    league_duration_stats = league_stats['duration_list']

    league_stats.update({'radiant_win_rate': f"{league_stats['radiant_win_rate'] * 100:.2f}%", 'dire_win_rate': f"{league_stats['dire_win_rate'] * 100:.2f}%"})
    league_stats.update({'avg_duration': f"{league_stats['avg_duration']: .2f} mins"})

    d2 = [d['duration'] for d in league_duration_stats]
    league_duration_stats = sorted(league_duration_stats, key=lambda x: x['duration'])
    t = league_duration_stats[0]['duration']
    max_duration = league_duration_stats[-1]['duration']
    while t <= max_duration:
        if t not in d2:
            league_duration_stats.append({'duration': t, 'count': 0})
        t = t + 5

    for d in league_duration_stats:
        d.update({'duration': f"{d['duration']: .0f} - {d['duration'] + 5: .0f} mins"})

    class ItemTableLeagueStats(Table):
        count = Col('total game count')
        avg_duration = Col('Average game duration')
        radiant_win_count = Col('radiant wins')
        radiant_win_rate = Col('radiant w%')
        dire_win_count = Col('dire wins')
        dire_win_rate = Col('dire w%')

    table_league_stats = ItemTableLeagueStats([league_stats])
    table_league_stats.table_id = 'table_league_stats'
    table_league_stats.classes = ['cell-border']

    class ItemTableLeagueDurationStats(Table):
        duration = Col('game duration')
        count = Col('count')

    table_league_duration_stats = ItemTableLeagueDurationStats(league_duration_stats)
    table_league_duration_stats.table_id = 'table_league_duration_stats'
    table_league_duration_stats.classes = ['display']

    return render_template("template_league_league_stats.html", table_league_stats=table_league_stats, league_info=league_info,
                           table_league_duration_stats=table_league_duration_stats)


@app.route('/league/<int:leagueid>/winner_stats', methods=['GET'])
def league_winner_stats(leagueid: int):
    league_info = query_league_by_id(db, leagueid)
    winner_stats = query_one_league_winner_stats(db, leagueid)
    for d in winner_stats:
        d.update({'winrate': f"{d['winrate'] * 100:.2f}%", 'winrate_bans': f"{d['winrate_bans'] * 100:.2f}%"})

    class ItemTableHeroStats(Table):
        hero_id = Col('hero ID')
        name = Col('hero name')
        picks = Col('picks')
        winrate = Col('winrate')
        bans = Col('bans')
        winrate_bans = Col('w% of bans')
        contests = Col('picks + bans')
        wins = Col('wins')
        losses = Col('losses')
        wins_of_bans = Col('wins of bans')

    table_winner_stats = ItemTableHeroStats(winner_stats)
    table_winner_stats.table_id = 'table_winner_stats'
    table_winner_stats.classes = ['display']

    if len(winner_stats) == 0:
        table_winner_stats = 'None'

    return render_template("template_league_winner_stats.html", league_info=league_info, table_winner_stats=table_winner_stats)


@app.route('/heroes', methods=['GET'])
def heroes():
    hero_stats = query_all_heroes_stats(db)
    for d in hero_stats:
        d.update({'winrate': f"{d['winrate'] * 100:.2f}%", 'winrate_bans': f"{d['winrate_bans'] * 100:.2f}%"})

    class ItemTableHeroStats(Table):
        hero_id = Col('hero ID')
        name = Col('hero name')
        contests = Col('picks + bans')
        picks = Col('picks')
        winrate = Col('winrate')
        bans = Col('bans')
        winrate_bans = Col('w% of bans')
        wins = Col('wins')
        losses = Col('losses')
        wins_of_bans = Col('wins of bans')

    table_all_hero_stats = ItemTableHeroStats(hero_stats)
    table_all_hero_stats.table_id = 'table_all_hero_stats'
    table_all_hero_stats.classes = ['display']

    return render_template("template_all_hero_stats.html", table_all_hero_stats=table_all_hero_stats)


@app.route('/hero/<int:hero_id>', methods=['GET'])
def hero_base(hero_id: int):
    return redirect(f"/hero/{hero_id}/league_stats")


@app.route('/hero/<int:hero_id>/league_stats', methods=['GET'])
def hero_league_stats(hero_id):
    hero_info = query_hero_by_id(db, hero_id)
    league_info = get_all_leagues(db)
    all_league_stats = query_all_leagues_stats(db)
    league_stats = query_one_hero_league_stats(db, hero_id)
    duration_stats = query_one_hero_duration_stats(db, hero_id)
    net_worth_stats = query_one_hero_net_worth_stats(db, hero_id)

    all_duration = ['(30- mins) Early game', '(30-40 mins) Mid game', '(40+ mins) Late game']

    # transform league stats
    d2 = [d['leagueid'] for d in league_stats]
    for d in all_league_stats:
        if d['leagueid'] not in d2:
            league_stats.append({'picks': 0, 'bans': 0, 'wins': 0, 'wins_of_bans': 0, 'losses': 0, 'contests': 0, 'winrate': 0,
                                 'winrate_bans': 0, 'leagueid': d['leagueid'], 'order': d['order'], 'name': d['name'], 'count': d['count']})

    for d in league_stats:
        d.update({'winrate': f"{d['winrate'] * 100:.2f}%", 'winrate_bans': f"{d['winrate_bans'] * 100:.2f}%"})

    for d in league_stats:
        if d['count'] > 0:
            d.update({'pickrate': f"{d['picks'] / d['count'] * 100:.2f}%", 'banrate': f"{d['bans'] / d['count'] * 100:.2f}%", 'activerate': f"{(d['picks'] + d['bans']) / d['count'] * 100:.2f}%"})
        else:
            d.update({'pickrate': f"{0:.2f}%", 'banrate': f"{0:.2f}%", 'activerate': f"{0:.2f}%"})

    # transform duration stats
    d2 = [d['type'] for d in duration_stats]
    for d in all_duration:
        if d not in d2:
            duration_stats.append({'type': d, 'picks': 0, 'wins': 0, 'losses': 0, 'winrate': 0})

    for d in duration_stats:
        d.update({'winrate': f"{d['winrate'] * 100:.2f}%"})

    # transform net worth stats
    d2 = [d['leagueid'] for d in net_worth_stats]
    for d in league_info:
        if d['leagueid'] not in d2:
            net_worth_stats.append({'leagueid': d['leagueid'], 'value': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}})

    d2 = {d['leagueid']: d for d in league_info}
    net_worth_stats = [dict(d, **d2.get(d['leagueid'], {})) for d in net_worth_stats]
    for d in net_worth_stats:
        d['count'] = 0
        for k, v in d['value'].items():
            d['rank' + k] = v
            d['count'] += v
        for k, v in d['value'].items():
            if d['count'] > 0:
                d['rank' + k + '_rate'] = v / d['count']
            else:
                d['rank' + k + '_rate'] = 0
            d['rank' + k + '_rate'] = f"{d['rank' + k + '_rate'] * 100:.2f}%"
        del d['value']

    # display league stats
    class ItemTableLeagueStats(Table):
        order = Col('order')
        leagueid = Col('league ID')
        name = Col('league name')
        count = Col('match count')
        activerate = Col('pick+ban rate')
        pickrate = Col('pick rate')
        banrate = Col('ban rate')
        winrate = Col('winrate')
        winrate_bans = Col('w% of bans')
        contests = Col('picks + bans')
        wins = Col('wins')
        bans = Col('bans')
        picks = Col('picks')
        losses = Col('losses')
        wins_of_bans = Col('wins of bans')

    table_league_stats = ItemTableLeagueStats(league_stats)
    table_league_stats.table_id = 'table_league_stats'
    table_league_stats.classes = ['display']

    # display duration stats
    class ItemTableDurationStats(Table):
        type = Col('game duration')
        winrate = Col('win rate')
        picks = Col('matches')
        wins = Col('wins')

    table_duration_stats = ItemTableDurationStats(duration_stats)
    table_duration_stats.table_id = 'table_duration_stats'
    table_duration_stats.classes = ['display']

    # display net worth stats
    class ItemTableNetWorthStats(Table):
        order = Col('order')
        leagueid = Col('league ID')
        name = Col('league name')
        count = Col('match count')
        rank1_rate = Col('1st %')
        rank2_rate = Col('2nd %')
        rank3_rate = Col('3rd %')
        rank4_rate = Col('4th %')
        rank5_rate = Col('5th %')
        rank1 = Col('1st')
        rank2 = Col('2nd')
        rank3 = Col('3rd')
        rank4 = Col('4th')
        rank5 = Col('5th')

    table_net_worth_stats = ItemTableNetWorthStats(net_worth_stats)
    table_net_worth_stats.table_id = 'table_net_worth_stats'
    table_net_worth_stats.classes = ['display']

    return render_template("template_hero_league_stats.html", hero_info=hero_info, table_league_stats=table_league_stats, table_duration_stats=table_duration_stats, table_net_worth_stats=table_net_worth_stats)


@app.route('/hero/<int:hero_id>/versus_stats', methods=['GET'])
def hero_versus_stats(hero_id):
    hero_info = query_hero_by_id(db, hero_id)
    versus_stats = query_one_hero_versus_stats(db, hero_id)

    # transform versus stats
    for d in versus_stats:
        d.update(d['value'])
        del d['value']
        d['with_match'] = d['with_win'] + d['with_lose']
        d['against_match'] = d['against_win'] + d['against_lose']
        d['ban_match'] = d['ban_win'] + d['ban_lose']
        if d['with_match'] > 0:
            d['with_rate'] = d['with_win'] / d['with_match']
        else:
            d['with_rate'] = 0
        if d['against_match'] > 0:
            d['against_rate'] = d['against_win'] / d['against_match']
        else:
            d['against_rate'] = 0
        if d['ban_match'] > 0:
            d['ban_rate'] = d['ban_win'] / d['ban_match']
        else:
            d['ban_rate'] = 0
        d.update({'with_rate': f"{d['with_rate'] * 100:.2f}%", 'against_rate': f"{d['against_rate'] * 100:.2f}%", 'ban_rate': f"{d['ban_rate'] * 100:.2f}%"})

    d1 = {d['hero_id']: d for d in query_all_hero_name(db)}
    versus_stats = [dict(d, **d1.get(d['hero_id'], {})) for d in versus_stats]

    # display versus_against stats
    class ItemTableVersusWithStats(Table):
        hero_id = Col('hero id')
        name = Col('hero name')
        with_rate = Col('win rate')
        with_match = Col('matches')
        with_win = Col('wins')
    
    class ItemTableVersusAgainstStats(Table):
        hero_id = Col('hero id')
        name = Col('hero name')
        against_rate = Col('win rate')
        against_match = Col('matches')
        against_win = Col('wins')
        
    class ItemTableVersusBanStats(Table):
        hero_id = Col('hero id')
        name = Col('hero name')
        ban_rate = Col('win rate')
        ban_match = Col('matches')
        ban_win = Col('wins')

    table_versus_against_stats = ItemTableVersusAgainstStats(versus_stats)
    table_versus_against_stats.table_id = 'table_versus_against_stats'
    table_versus_against_stats.classes = ['display']

    table_versus_with_stats = ItemTableVersusWithStats(versus_stats)
    table_versus_with_stats.table_id = 'table_versus_with_stats'
    table_versus_with_stats.classes = ['display']

    table_versus_ban_stats = ItemTableVersusBanStats(versus_stats)
    table_versus_ban_stats.table_id = 'table_versus_ban_stats'
    table_versus_ban_stats.classes = ['display']

    return render_template("template_hero_versus_stats.html", hero_info=hero_info, table_versus_against_stats=table_versus_against_stats, table_versus_with_stats=table_versus_with_stats, table_versus_ban_stats=table_versus_ban_stats)


@app.route('/hero/<string:hero_name>', methods=['GET'])
def hero_info_by_name(hero_name: str):
    return hero_name


@app.route('/test', methods=['GET'])
def test():
    return render_template("test_template.html")


app.run()
