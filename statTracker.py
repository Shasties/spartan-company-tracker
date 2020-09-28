#!/usr/bin/python3
import json, sys, os
import http.client, urllib.request, urllib.parse, urllib.error, base64

# Return IDs of Game Modes that contribute towards Achilles
def initAchillesModes():
    return [
        ""
    ]

# Return IDs of Spartan Medals that count towards Achilles
def initSpartanMedals():
    return [
        ""
    ]

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
            print("{0} - {1} / {2}".format(l['name'], comm_mapping[l['commendation_id']]['progress'], l['threshold']))

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
        company = getCompany(conn,header,"CrankiestSeeker")
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
        if armor_prog < 100:
            displayArmorProg(company_commendation,company_commendation_metadata)
        print("Progress to Achilles Helmet: {:.2f}%".format(helmet_prog))
        if helmet_prog < 100:
            displayHelmetProg(company_commendation,company_commendation_metadata)

        ## TODO - Handle Member contributions ##
        print("Calculating Individual Contributions...")
        try:
            os.mkdir(output_dir)
        except Exception as e:
            pass
        # TODO
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
