from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from bson import Code
from bson.son import SON


def get_all_heroes(db: Database) -> list:
    """ get heroes table """
    collection = db['heroes']
    return list(collection.find())


def get_all_leagues(db: Database) -> list:
    """ get leagues table"""
    collection = db['leagues']
    return list(collection.find())


def query_all_hero_name(db: Database) -> list:
    """ get list of dictionaries of hero_id to hero name"""
    collection = db['heroes']
    pipeline = [
        {
            '$project': {
                '_id': 0,
                'hero_id': 1,
                'name': '$localized_name'
            }
        }
    ]
    return list(collection.aggregate(pipeline))


def query_hero_by_id(db: Database, heroid: int) -> dict:
    collection = db['heroes']
    condition = {'hero_id': heroid}
    list_hero = list(collection.find(condition))
    return list_hero[0]


def query_hero_by_name(db: Database, name: str) -> dict:
    collection = db['heroes']
    condition = {'localized_name': name}
    list_hero = list(collection.find(condition))
    return list_hero[0]


def query_league_by_id(db: Database, leagueid: int) -> dict:
    collection = db['leagues']
    condition = {"leagueid": leagueid}
    list_league = list(collection.find(condition))
    return list_league[0]


def query_all_leagues_stats(db: Database) -> list:
    collection = db['matches']
    pipeline = [
        {
            '$match': {
                'radiant_win': {
                    '$ne': None
                },
                'picks_bans': {
                    '$ne': None
                }
            }
        }, {
            '$project': {
                'duration': 1,
                'leagueid': 1,
                'radiant_win': 1
            }
        }, {
            '$group': {
                '_id': '$leagueid',
                'count': {
                    '$sum': 1
                },
                'duration': {
                    '$sum': '$duration'
                },
                'radiant_win_count': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$radiant_win', True
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'duration': {
                    '$sum': '$duration'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'leagueid': '$_id',
                'duration_list': 1,
                'count': 1,
                'radiant_win_count': 1,
                'avg_duration': {
                    '$divide': [
                        {
                            '$divide': [
                                '$duration', 60
                            ]
                        }, '$count'
                    ]
                },
                'dire_win_count': {
                    '$subtract': [
                        '$count', '$radiant_win_count'
                    ]
                },
                'radiant_win_rate': {
                    '$divide': [
                        '$radiant_win_count', '$count'
                    ]
                },
                'dire_win_rate': {
                    '$subtract': [
                        1, {
                            '$divide': [
                                '$radiant_win_count', '$count'
                            ]
                        }
                    ]
                }
            }
        }, {
            '$lookup': {
                'from': 'leagues',
                'localField': 'leagueid',
                'foreignField': 'leagueid',
                'as': 'league'
            }
        }, {
            '$replaceRoot': {
                'newRoot': {
                    '$mergeObjects': [
                        '$$ROOT', {
                            '$arrayElemAt': [
                                '$league', 0
                            ]
                        }
                    ]
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'league': 0
            }
        }
    ]
    return list(collection.aggregate(pipeline))


def query_all_heroes_stats(db: Database) -> list:
    """ hero info combined of all leagues """
    return query_one_league_hero_stats(db, {'$ne': None})


def query_one_league_league_stats(db: Database, leagueid: int) -> dict:
    """ league stats"""
    collection = db['matches']
    pipeline = [
        {
            '$match': {
                'leagueid': leagueid,
                'radiant_win': {
                    '$ne': None
                },
                'picks_bans': {
                    '$ne': None
                }
            }
        }, {
            '$project': {
                'radiant_win': 1,
                'duration': 1
            }
        }, {
            '$group': {
                '_id': {
                    'duration': {
                        '$multiply': [
                            {
                                '$trunc': {
                                    '$divide': [
                                        '$duration', 300
                                    ]
                                }
                            }, 5
                        ]
                    }
                },
                'count': {
                    '$sum': 1
                },
                'radiant_win_count': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$radiant_win', True
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'duration': {
                    '$sum': '$duration'
                }
            }
        }, {
            '$group': {
                '_id': None,
                'duration_list': {
                    '$addToSet': {
                        'duration': '$_id.duration',
                        'count': '$count'
                    }
                },
                'count': {
                    '$sum': '$count'
                },
                'radiant_win_count': {
                    '$sum': '$radiant_win_count'
                },
                'duration': {
                    '$sum': '$duration'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'duration_list': 1,
                'count': 1,
                'radiant_win_count': 1,
                'avg_duration': {
                    '$divide': [
                        {
                            '$divide': [
                                '$duration', 60
                            ]
                        }, '$count'
                    ]
                },
                'dire_win_count': {
                    '$subtract': [
                        '$count', '$radiant_win_count'
                    ]
                },
                'radiant_win_rate': {
                    '$divide': [
                        '$radiant_win_count', '$count'
                    ]
                },
                'dire_win_rate': {
                    '$subtract': [
                        1, {
                            '$divide': [
                                '$radiant_win_count', '$count'
                            ]
                        }
                    ]
                }
            }
        }
    ]
    return list(collection.aggregate(pipeline))[0]


def query_one_league_hero_stats(db: Database, leagueid: int) -> list:
    """ hero pick/ban/contest/win/loss stats"""
    collection = db['matches']
    pipeline = [
        {
            '$match': {
                'leagueid': leagueid,
                'radiant_win': {
                    '$ne': None
                },
                'picks_bans': {
                    '$ne': None
                }
            }
        }, {
            '$project': {
                'picks_bans': 1,
                'radiant_win': 1
            }
        }, {
            '$unwind': {
                'path': '$picks_bans'
            }
        }, {
            '$project': {
                'hero_id': '$picks_bans.hero_id',
                'is_pick': '$picks_bans.is_pick',
                'team': '$picks_bans.team',
                'radiant_win': 1
            }
        }, {
            '$group': {
                '_id': '$hero_id',
                'picks': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$is_pick', True
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'bans': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$is_pick', True
                                ]
                            }, 0, 1
                        ]
                    }
                },
                'wins': {
                    '$sum': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', True
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 0
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', False
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 1
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'wins_of_bans': {
                    '$sum': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', True
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 0
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', False
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', False
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 1
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', False
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }, 1, 0
                        ]
                    }
                }
            }
        }, {
            '$addFields': {
                'losses': {
                    '$subtract': [
                        '$picks', '$wins'
                    ]
                },
                'contests': {
                    '$add': [
                        '$picks', '$bans'
                    ]
                },
                'winrate': {
                    '$cond': [
                        {
                            '$ne': [
                                '$picks', 0
                            ]
                        }, {
                            '$divide': [
                                '$wins', '$picks'
                            ]
                        }, 0
                    ]
                },
                'winrate_bans': {
                    '$cond': [
                        {
                            '$ne': [
                                '$bans', 0
                            ]
                        }, {
                            '$divide': [
                                '$wins_of_bans', '$bans'
                            ]
                        }, 0
                    ]
                },
                'hero_id': '$_id'
            }
        }, {
            '$project': {
                '_id': 0
            }
        }
    ]
    result = list(collection.aggregate(pipeline))

    d1 = {d['hero_id']: d for d in query_all_hero_name(db)}
    result = [dict(d, **d1.get(d['hero_id'], {})) for d in result]
    return result


def query_one_league_all_hero_inactive(db: Database, leagueid: int) -> list:
    """ hero id where hero is not picked and banned"""
    collection = db['matches']
    pipeline = [
        {
            '$match': {
                'leagueid': leagueid,
                'radiant_win': {
                    '$ne': None
                },
                'picks_bans': {
                    '$ne': None
                }
            }
        }, {
            '$project': {
                'picks_bans': 1
            }
        }, {
            '$unwind': {
                'path': '$picks_bans'
            }
        }, {
            '$project': {
                'hero_id': '$picks_bans.hero_id'
            }
        }, {
            '$group': {
                '_id': '$hero_id'
            }
        }, {
            '$out': 'temp_hero_active'
        }
    ]
    collection.aggregate(pipeline)

    # pipeline = [
    #     {
    #         '$match': {
    #             'leagueid': leagueid,
    #             'radiant_win': {
    #                 '$ne': None
    #             },
    #             'picks_bans': {
    #                 '$ne': None
    #             }
    #         }
    #     }, {
    #         '$project': {
    #             'picks_bans': 1
    #         }
    #     }, {
    #         '$unwind': {
    #             'path': '$picks_bans'
    #         }
    #     }, {
    #         '$project': {
    #             'hero_id': '$picks_bans.hero_id'
    #         }
    #     }, {
    #         '$group': {
    #             '_id': '$hero_id'
    #         }
    #     }
    # ]
    # try:
    #     db.command({
    #         'create': 'temp_view_hero_active',
    #         'viewOn': 'matches',
    #         'pipeline': pipeline
    #     }
    #     )
    # except:
    #     pass

    collection = db['heroes']
    pipeline = [
        {
            '$project': {
                'hero_id': 1,
                'localized_name': 1
            }
        }, {
            '$lookup': {
                'from': 'temp_hero_active',  # 'from': 'temp_view_hero_active'
                'localField': 'hero_id',
                'foreignField': '_id',
                'as': 'a'
            }
        }, {
            '$match': {
                'a': {
                    '$size': 0
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'hero_id': 1
            }
        }
    ]
    result = list(collection.aggregate(pipeline))

    collection = db['temp_hero_active']
    collection.drop()

    # collection = db['temp_view_hero_active']
    # collection.drop()

    d1 = {d['hero_id']: d for d in query_all_hero_name(db)}
    result = [dict(d, **d1.get(d['hero_id'], {})) for d in result]
    return result


def query_one_league_winner_stats(db: Database, leagueid: int) -> list:
    """ hero stats of winner team"""
    collection = db['leagues']
    condition = {'leagueid': leagueid}
    projection = {'winner': 1}
    result = list(collection.find(condition, projection))
    winner = result[0]['winner']

    collection = db['matches']
    pipeline = [
        {
            '$match': {
                'radiant_win': {
                    '$ne': None
                },
                'picks_bans': {
                    '$ne': None
                },
                'leagueid': leagueid,
                '$or': [
                    {
                        'radiant_team.name': winner
                    }, {
                        'dire_team.name': winner
                    }
                ]
            }
        }, {
            '$project': {
                'picks_bans': 1,
                'radiant_win': 1
            }
        }, {
            '$unwind': {
                'path': '$picks_bans'
            }
        }, {
            '$project': {
                'hero_id': '$picks_bans.hero_id',
                'is_pick': '$picks_bans.is_pick',
                'team': '$picks_bans.team',
                'radiant_win': 1
            }
        }, {
            '$group': {
                '_id': '$hero_id',
                'picks': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$is_pick', True
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'bans': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$is_pick', True
                                ]
                            }, 0, 1
                        ]
                    }
                },
                'wins': {
                    '$sum': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', True
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 0
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', False
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 1
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'wins_of_bans': {
                    '$sum': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', True
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 0
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', False
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', False
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 1
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', False
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }, 1, 0
                        ]
                    }
                }
            }
        }, {
            '$addFields': {
                'losses': {
                    '$subtract': [
                        '$picks', '$wins'
                    ]
                },
                'contests': {
                    '$add': [
                        '$picks', '$bans'
                    ]
                },
                'winrate': {
                    '$cond': [
                        {
                            '$ne': [
                                '$picks', 0
                            ]
                        }, {
                            '$divide': [
                                '$wins', '$picks'
                            ]
                        }, 0
                    ]
                },
                'winrate_bans': {
                    '$cond': [
                        {
                            '$ne': [
                                '$bans', 0
                            ]
                        }, {
                            '$divide': [
                                '$wins_of_bans', '$bans'
                            ]
                        }, 0
                    ]
                },
                'hero_id': '$_id'
            }
        }, {
            '$project': {
                '_id': 0
            }
        }
    ]
    result = list(collection.aggregate(pipeline))

    d1 = {d['hero_id']: d for d in query_all_hero_name(db)}
    result = [dict(d, **d1.get(d['hero_id'], {})) for d in result]
    return result


def query_one_hero_league_stats(db: Database, heroid: int) -> list:
    """ one hero stats of all leagues """
    collection = db['matches']
    pipeline = [
        {
            '$match': {
                'radiant_win': {
                    '$ne': None
                },
                'picks_bans': {
                    '$ne': None
                }
            }
        }, {
            '$project': {
                'leagueid': 1,
                'picks_bans': 1,
                'radiant_win': 1
            }
        }, {
            '$unwind': {
                'path': '$picks_bans'
            }
        }, {
            '$project': {
                'leagueid': 1,
                'hero_id': '$picks_bans.hero_id',
                'is_pick': '$picks_bans.is_pick',
                'team': '$picks_bans.team',
                'radiant_win': 1
            }
        }, {
            '$match': {
                'hero_id': heroid
            }
        }, {
            '$group': {
                '_id': '$leagueid',
                'picks': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$is_pick', True
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'bans': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$is_pick', True
                                ]
                            }, 0, 1
                        ]
                    }
                },
                'wins': {
                    '$sum': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', True
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 0
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', False
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 1
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'wins_of_bans': {
                    '$sum': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', True
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 0
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', False
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', False
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 1
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', False
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }, 1, 0
                        ]
                    }
                }
            }
        }, {
            '$addFields': {
                'losses': {
                    '$subtract': [
                        '$picks', '$wins'
                    ]
                },
                'contests': {
                    '$add': [
                        '$picks', '$bans'
                    ]
                },
                'winrate': {
                    '$cond': [
                        {
                            '$ne': [
                                '$picks', 0
                            ]
                        }, {
                            '$divide': [
                                '$wins', '$picks'
                            ]
                        }, 0
                    ]
                },
                'winrate_bans': {
                    '$cond': [
                        {
                            '$ne': [
                                '$bans', 0
                            ]
                        }, {
                            '$divide': [
                                '$wins_of_bans', '$bans'
                            ]
                        }, 0
                    ]
                },
                'leagueid': '$_id'
            }
        }, {
            '$project': {
                '_id': 0
            }
        }
    ]
    result = list(collection.aggregate(pipeline))

    d1 = {d['leagueid']: d for d in query_all_leagues_stats(db)}
    result = [dict(d, **d1.get(d['leagueid'], {})) for d in result]
    return result


def query_one_hero_duration_stats(db: Database, heroid: int) -> list:
    """ hero duration stats"""
    collection = db['matches']
    pipeline = [
        {
            '$match': {
                'radiant_win': {
                    '$ne': None
                },
                'picks_bans': {
                    '$ne': None
                }
            }
        }, {
            '$project': {
                'picks_bans': 1,
                'radiant_win': 1,
                'duration': 1
            }
        }, {
            '$unwind': {
                'path': '$picks_bans'
            }
        }, {
            '$project': {
                'leagueid': 1,
                'hero_id': '$picks_bans.hero_id',
                'is_pick': '$picks_bans.is_pick',
                'team': '$picks_bans.team',
                'radiant_win': 1,
                'duration': 1
            }
        }, {
            '$match': {
                'hero_id': heroid
            }
        }, {
            '$group': {
                '_id': {
                    '$cond': [
                        {
                            '$gt': [
                                '$duration', 2400
                            ]
                        }, '(40+ mins) Late game', {
                            '$cond': [
                                {
                                    '$lte': [
                                        '$duration', 1800
                                    ]
                                }, '(30- mins) Early game', '(30-40 mins) Mid game'
                            ]
                        }
                    ]
                },
                'picks': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$is_pick', True
                                ]
                            }, 1, 0
                        ]
                    }
                },
                'wins': {
                    '$sum': {
                        '$cond': [
                            {
                                '$or': [
                                    {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', True
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 0
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$radiant_win', False
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$team', 1
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$is_pick', True
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }, 1, 0
                        ]
                    }
                }
            }
        }, {
            '$addFields': {
                'losses': {
                    '$subtract': [
                        '$picks', '$wins'
                    ]
                },
                'winrate': {
                    '$cond': [
                        {
                            '$ne': [
                                '$picks', 0
                            ]
                        }, {
                            '$divide': [
                                '$wins', '$picks'
                            ]
                        }, 0
                    ]
                },
                'type': '$_id'
            }
        }, {
            '$project': {
                '_id': 0
            }
        }
    ]
    return list(collection.aggregate(pipeline))


def query_one_hero_net_worth_stats(db: Database, heroid: int) -> list:
    collection = db['matches']
    with open('mapreduce_javascript/map_net_worth.js') as f:
        map_func = Code(f.read().replace('{HERO_ID}', str(heroid)))

    with open('mapreduce_javascript/reduce_net_worth.js') as f:
        reduce_func = Code(f.read())
    options = SON([('inline', 1)])
    result = collection.map_reduce(map_func, reduce_func, options)
    result = result['results']
    for d in result:
        d.update({'leagueid': int(d['_id'])})
        del d['_id']
        for k, v in d['value'].items():
            d['value'][k] = int(v)
    return result


def query_one_hero_versus_stats(db: Database, heroid: int) -> list:
    collection = db['matches']
    with open('mapreduce_javascript/map_versus.js') as f:
        map_func = Code(f.read().replace('{HERO_ID}', str(heroid)))

    with open('mapreduce_javascript/reduce_versus.js') as f:
        reduce_func = Code(f.read())
    options = SON([('inline', 1)])
    result = collection.map_reduce(map_func, reduce_func, options)
    result = result['results']
    for d in result:
        d.update({'hero_id': int(d['_id'])})
        del d['_id']
        for k, v in d['value'].items():
            d['value'][k] = int(v)
    return result


if __name__ == '__main__':
    # connect MongoDB as client
    client = MongoClient('localhost', 27017)

    # use database
    db = client['project']

    a = query_one_hero_versus_stats(db, 1)
    for each in a:
        print(each)
