#!/usr/bin/python3
import json, sys
import http.client, urllib.request, urllib.parse, urllib.error, base64

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

#TODO
def getArmorProg(company_commendations, meta_commendations):
    pass

#TODO
def getHelmetProg(company_commendations, meta_commendations):
    pass

# Source api key from file
def sourceCredentials(input_file="./source.json"):
    with open(input_file,"r") as f:
        return json.load(f)

def readMetadata(source_file="./comp_comm_metadata_formatted.json"):
    with open(source_file,"r") as f:
        return json.load(f)

def main():
    conn = ""
    try:
        conn = http.client.HTTPSConnection('www.haloapi.com')
        print("Connected to Halo API")
    except Exception as e:
        print("cannot connect to haloapi.com")
        print(e)
    try:
        data = sourceCredentials()
        company_commendation_metadata = readMetadata()
        header = {'Ocp-Apim-Subscription-Key':data['api_key']}
        company = getCompany(conn,header,"CrankiestSeeker")
        print("Gathering data for Spartan Company: %s" % company['Name'])
        company_info = getCompanyInfo(conn,header,company['Id'])
        company_commendation = getCompanyComm(conn,header,company['Id'])
        print("Overview for Spartan Company %s" % company['Name'])
        print("Leader: %s" % company_info['Creator']['Gamertag'])
        print("Total Members: %s" % len(company_info['Members']))
        armor_prog = getArmorProg(company_commendation,company_commendation_meta)
        print("Progress to Achilles Armor: %s" % armor_prog)
        helmet_prog = getHelmetProg(company_commendation,company_commendation_meta)
        print("Progress to Achilles Helmet: %s" & helmet_prog)
        ## TODO - Handle Member contributions ##
    except Exception as e:
        print("Error while performing operations")
        print(e)
    try:
        conn.close()
    except Exception as e:
        print("Error while closing connection")
        print(e)


if __name__ == "__main__":
    main()
