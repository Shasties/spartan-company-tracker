#!/usr/bin/python3
import json, sys, os, time, datetime
import http.client, urllib.request, urllib.parse, urllib.error, base64
import datetime,requests

#print(my_date.isoformat())

# Return IDs of Game Modes that contribute towards Achilles
def initAchillesModes():
    return [
        "arena",
        "warzone"
    ]

# Returns mapping of which company commendation ID is incremented by set of spartan commendation IDs
def initSpartanMapping(mode):
    if 'warzone' in mode:
        return {
                'bfa2d856-dd46-4f26-827c-60564bd5d8cd':['858c8372-7879-4ee1-ba81-3213f1e9da0f'], # Sorry Mate 
                '902bd019-b9d2-4848-a6a3-9b2cea498bf0':['4204396686'], # Forgot to pay the toll
                '96179e21-1374-48a7-bfd3-e66759c69278':['216ed14e-e005-42b4-b445-a1385c796a50'], # From the top rope
                'e9f58e96-301b-4d58-9621-36fcea05a6a2':[ # Standard Issue
                    '61217e0a-832e-487b-9f3b-51b36a6803c7', # Assault Rifle
                    '6d0d92dc-59a8-430c-9cd1-9e024e35a514', # Battle Rifle
                    'c9bcb904-607f-42ea-acae-4cbdcdf65143', # DMR
                    'f33f1aec-59ad-47eb-be13-fd0e654a53aa', # Pistol
                    '3c357b49-4860-48b7-9d92-dfdfd9931b49', # SMG
                    # No H2 BR?
                    ],
                '02bf07b9-2041-48a4-802d-818955b8df21':['ab7c2b82-1c4b-4ba8-accf-0dfc5cf2ff77'], # The Pain Train
                'd7205f89-37b3-47fe-a1a6-6fe487fe50b3':['ad36d0cd-7e44-49a2-8a2c-c103a38f17d8'], # I'm Just Perfect
                'f95a9909-53b2-4b08-8c12-88ac7e20c7d2':[# Road Trip
                    'd3e8e2da-8e7c-4655-b238-d57db7bc9836', # Warthog
                    # Mongoose ?
                    'c41eb798-ca34-4ff4-95a1-9a67f2a2ccd3', # Scorpion
                    '16dbe561-7201-4c76-9d71-e6c27945e554', # Ghost
                    '71e867d7-51dc-484a-936e-33c8efb5a219', # Wraith
                    ], 
                '9a778521-c93d-4d43-89a7-7d23d86eaabd':[ # Look ma no pin
                    'a7b68c66-7195-401d-9f82-df4da96b66c3', # Splinter Grenade
                    '79b6e993-ff9b-4a53-9789-cccaf86a4e22', # Frag Grenade
                    '5f0fb4c9-19e6-44bf-a751-f254a5de8adc' # Plasma Grenade
                    ]
        }
    else:
        return {
                '96179e21-1374-48a7-bfd3-e66759c69278':['216ed14e-e005-42b4-b445-a1385c796a50'], # From the top rope
                'e9f58e96-301b-4d58-9621-36fcea05a6a2':[ # Standard Issue
                    '61217e0a-832e-487b-9f3b-51b36a6803c7', # Assault Rifle
                    '6d0d92dc-59a8-430c-9cd1-9e024e35a514', # Battle Rifle
                    'c9bcb904-607f-42ea-acae-4cbdcdf65143', # DMR
                    'f33f1aec-59ad-47eb-be13-fd0e654a53aa', # Pistol
                    '3c357b49-4860-48b7-9d92-dfdfd9931b49', # SMG
                    # No H2 BR?
                    ],
                '02bf07b9-2041-48a4-802d-818955b8df21':['ab7c2b82-1c4b-4ba8-accf-0dfc5cf2ff77'], # The Pain Train
                'd7205f89-37b3-47fe-a1a6-6fe487fe50b3':['ad36d0cd-7e44-49a2-8a2c-c103a38f17d8'], # I'm Just Perfect
                '9a778521-c93d-4d43-89a7-7d23d86eaabd':[ # Look ma no pin
                    'a7b68c66-7195-401d-9f82-df4da96b66c3', # Splinter Grenade
                    '79b6e993-ff9b-4a53-9789-cccaf86a4e22', # Frag Grenade
                    '5f0fb4c9-19e6-44bf-a751-f254a5de8adc' # Plasma Grenade
                    ]
                }

# Get commendations from single game
def getGameComms(game,gamertag,headers):
    try:
        response = requests.get("https://www.haloapi.com/stats/{0}".format(game['Links']['StatsMatchDetails']['Path']),headers=headers)
        json_response = response.json()
    
        for player in json_response['PlayerStats']:
            if player['Player']['Gamertag'] == gamertag:
                return player
    except Exception as e:
        print("Api rate limit reached - pausing for 10s")
        time.sleep(10)
        return getGameComms(game,gamertag,headers)

# Get commendations from all spartans for all games
def getSpartanComms(game_dict,company_commendations,conn,headers):
    inProgressComms = []
    # Find in progress commendations
    for commendation in company_commendations:
        if not company_commendations[commendation]['completed']:
            inProgressComms.append(company_commendations[commendation])

    total_comms = {}
    # Find earned commendations 
    for player in game_dict:
        playerProg = {}
        for game in game_dict[player]['Relevant_Games']:
            game_stats = getGameComms(game,player,headers)
            earned_comms = {}
            for comm_delta in game_stats['ProgressiveCommendationDeltas']:
                earned_comms[comm_delta['Id']] = int(comm_delta['Progress']) - int(comm_delta['PreviousProgress'])

            # Compare earned commendations to in progress commendations
            comm_mapping = initSpartanMapping(game['Links']['StatsMatchDetails']['Path'])
            for i in inProgressComms:
                cid = i['commendation_id']
                if cid in comm_mapping.keys():
                    # for all player commendations that count towards company commendation
                    for a in comm_mapping[cid]:
                        # if player has earned commendation, add to playerProg dictionary
                        if a in earned_comms.keys():
                            if i['name'] in playerProg.keys():
                                playerProg[i['name']] = playerProg[i['name']] + earned_comms[a]
                            else:
                                playerProg[i['name']] = earned_comms[a]
        total_comms[player] = playerProg
    return total_comms


# Get Length of Time Members Have Been Part of Company
def getMemberLength(members,output_dir):
    output_file = output_dir+"/joined_dates.json"
    new_dict = {}
    for member in members:
        new_dict[member['Player']['Gamertag']] = {'Joined': member['JoinedDate']['ISO8601Date'].split("T")[0]}

    with open(output_file,"w") as f:
        json.dump(new_dict,f,indent=4,sort_keys=True)

    return new_dict

# Recursive Function for formatting + making calls for specific player
def getRelevantGames(member,conn,headers,start_date,total_games=[],increment=0):
    params = urllib.parse.urlencode({
    # Request parameters
    'modes': ','.join(initAchillesModes()),
    'start': increment,
    'include-times': True,
    })
    gamertag = member['Player']['Gamertag'].replace(" ","%20")
    conn.request("GET", "/stats/h5/players/{0}/matches?{1}".format(gamertag,params), "{body}", headers)
    response = conn.getresponse()
    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    if 'statusCode' in json_obj.keys():
        print("api rate limit reached - stopping at increment {0}".format(increment))
        time.sleep(10)
        return getRelevantGames(member,conn,headers,start_date,total_games=total_games,increment=increment)
    relevant_matches = []
    for match in json_obj['Results']:
        # Subtract one day due to time API takes to register match as being completed
        #if (datetime.datetime.strptime(match["MatchCompletedDate"]["ISO8601Date"].split('T')[0],"%Y-%m-%d")-datetime.timedelta(days=1)).date() >= start_date:
        if datetime.datetime.strptime(match["MatchCompletedDate"]["ISO8601Date"].split('T')[0],"%Y-%m-%d").date() >= start_date:
            relevant_matches.append(match)
    total_games = total_games + relevant_matches
    # Can only grab 25 matches per call
    if len(relevant_matches) == 25 :
        return getRelevantGames(member,conn,headers,start_date,total_games,increment=increment+25)
    else:
        return total_games

# Get Number of Achilles Game Modes played in Last X Time - Defaults to 1 week
def getMemberGames(members,output_dir,conn,headers,time_delta=1,filter_list=[]):
    output_file = output_dir+"/played_matches.json"
    today = datetime.date.today()
    weekday = today.weekday()
    start_delta = datetime.timedelta(weeks=time_delta)
    member_dict = {}
    for member in members:
        if (filter_list == []) or (member['Player']['Gamertag'] in filter_list):
            start_of_week = today - start_delta
            print("Getting stats for {0}".format(member['Player']['Gamertag']))
            # If member joined within start time
            if datetime.datetime.strptime(member['JoinedDate']['ISO8601Date'].split('T')[0],"%Y-%m-%d").date() > start_of_week:
                start_of_week =  datetime.datetime.strptime(member['JoinedDate']['ISO8601Date'].split('T')[0],'%Y-%m-%d').date()
            # Retrieve player games
            try: 
                relevant_games = getRelevantGames(member,conn,headers,start_of_week)
                member_dict[member['Player']['Gamertag']] = {'Relevant_Games': relevant_games}
                member_dict[member['Player']['Gamertag']]['Number_Relevant_Games'] = len(relevant_games)
            except Exception as e:
                print(e)
    return member_dict

# Get Company from Gamertag
def getCompany(conn,headers,player):
    try:
        conn.request("GET", "/profile/h5/profiles/%s/appearance" % player, "{body}", headers)
        response = conn.getresponse()
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        return json_obj['Company']
    except Exception as e:
        print("Unable to perform REQUEST")
        print(e)
        sys.exit(1)

# Get Company information from ID
def getCompanyInfo(conn,headers,company_id):
    try:
        conn.request("GET", "/stats/h5/companies/%s" % company_id, "{body}", headers)
        response = conn.getresponse()
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        return json_obj
    except Exception as e:
        print("Unable to perform REQUEST")
        print(e)
        sys.exit(1)

# Get Company Commendation info
def getCompanyComm(conn,headers,company_id):
    try:
        conn.request("GET", "/stats/h5/companies/%s/commendations" % company_id, "{body}", headers)
        response = conn.getresponse()
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        return json_obj
    except Exception as e:
        print("Unable to perform REQUEST")
        print(e)
        sys.exit(1)

# Calculate how many levels are needed for Achilles Armor
def getArmorProg(company_commendations):
    for item in company_commendations['MetaCommendations']:
        if item['Id'] == "0a271639-6401-4c7a-a966-75519d5126f2": ## All Together Now
            return len(item['MetRequirements'])/31*100

# Calculate how many levels are needed for Achilles Helmet
def getHelmetProg(company_commendations):
    for item in company_commendations['MetaCommendations']:
        if item['Id'] == "7541e38a-5ffa-45e0-b551-cd00c428ca39": ## The Sum Is Greather Than The Parts
            return len(item['MetRequirements'])/31*100

# Source api key from file
def sourceCredentials(input_file="./source.json"):
    with open(input_file,"r") as f:
        return json.load(f)

# Read metadata for kinds of company commendations
def readMetadata(source_file="./comp_comm_metadata_formatted.json"):
    with open(source_file,"r") as f:
        return json.load(f)

# Display Achilles Armor Progress
def displayArmorProg(company_commendations,meta_commendations):
    # Only show information for commendations that are still needed
    kill_commendations = meta_commendations["0a271639-6401-4c7a-a966-75519d5126f2"]['requiredLevels']
    print(company_commendations)
    remaining_commendations = {}
    for c in company_commendations:
        if c['Id'] in kill_commendations:
            pass
    print("*** Remaining Armor Commendation Progress ***")

# Display Achilles Helmet Progress
def displayHelmetProg(company_commendations,meta_commendations):
    # Only show information for commendations that are still needed
    kill_commendations = meta_commendations["7541e38a-5ffa-45e0-b551-cd00c428ca39"]['requiredLevels']
    level_mapping = {}
    comm_mapping = {}
    # Map Level to Commendation Names
    for m in meta_commendations:
        if meta_commendations[m]['type'] == "Progressive" and meta_commendations[m]['category']['name'] == 'Kill':
            last_level = meta_commendations[m]['levels'][-1]
            level_mapping[last_level['id']] = {'commendation_id': m, 'name': meta_commendations[m]['name'], 'completed': False,'threshold': last_level['threshold']}
            comm_mapping[m] = {'name': meta_commendations[m]['name']}

    # Search for all required levels in completed levels
    for k in kill_commendations:
        for c in company_commendations['ProgressiveCommendations']:
            if len(c['CompletedLevels'])>1 and k['id'] == c['CompletedLevels'][-1]['Id']:
                level_mapping[k['id']]['completed'] = True
            elif c['Id'] in comm_mapping.keys(): 
                comm_mapping[c['Id']]['progress'] = c['Progress']

    print("*** Remaining Helmet Commendation Progress ***")
    for level in level_mapping:
        if not level_mapping[level]['completed']:
            l = level_mapping[level]
            l['progress'] = comm_mapping[l['commendation_id']]['progress']
            print("{0} - {1} / {2}".format(l['name'], l['progress'], l['threshold']))
    return level_mapping

# Main Function
def main():
    conn = ""
    # Connect to haloapi.com
    try:
        conn = http.client.HTTPSConnection('www.haloapi.com')
        print("Connected to Halo API")
    except Exception as e:
        print("cannot connect to haloapi.com")
        print(e)
    # Perform Data Gathering
    try:
        # Overview
        data = sourceCredentials()
        company_commendation_metadata = readMetadata()
        output_dir = "./output"
        header = {'Ocp-Apim-Subscription-Key':data['api_key']}
        company = getCompany(conn,header,data['player_of_company'])
        print("Gathering data for Spartan Company: %s" % company['Name'])
        company_info = getCompanyInfo(conn,header,company['Id'])
        company_commendation = getCompanyComm(conn,header,company['Id'])
        print("--- Overview for Spartan Company %s ---" % company['Name'])
        print("Leader: %s" % company_info['Creator']['Gamertag'])
        print("Total Members: %s" % len(company_info['Members']))
        armor_prog = getArmorProg(company_commendation)
        helmet_prog = getHelmetProg(company_commendation)

        # Achilles Completion
        print("Achilles Armor Completion: {:.2f}%".format(armor_prog))
        #TODO
        #if armor_prog < 100:
        #    displayArmorProg(company_commendation,company_commendation_metadata)
        print("Progress to Achilles Helmet: {:.2f}%".format(helmet_prog))
        progress = ""
        if helmet_prog < 100:
            progress = displayHelmetProg(company_commendation,company_commendation_metadata)

        print("Calculating Individual Contributions...")
        # Create output directory
        try:
            os.mkdir(output_dir)
        except Exception as e:
            pass

        # Length of Time Players have been Members
        members_dict = getMemberLength(company_info['Members'],output_dir)
        # Get Matches within past X time
        games_dict = getMemberGames(company_info['Members'],output_dir,conn,header,filter_list=data['filter_players'])
        for member in games_dict:
            members_dict[member].update(games_dict[member])
        # Get Medals of Matches 
        commendation_dict = getSpartanComms(games_dict,progress,conn,header)
        for member in commendation_dict:
            members_dict[member].update(commendation_dict[member])

        # Cleanup data structure
        for member in members_dict:
            members_dict[member].pop('Relevant_Games',None)

        # Write to output
        with open(output_dir+"/overall.json","w") as f:
            json.dump(members_dict,f,indent=4,sort_keys=True)

        print("See output under: {0}".format(output_dir))

    except Exception as e:
        print("Error while performing operations")
        print(e)

    # Try to close connection
    try:
        conn.close()
    except Exception as e:
        print("Error while closing connection")
        print(e)


if __name__ == "__main__":
    main()
