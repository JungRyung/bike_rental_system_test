import requests
import json
import time
import os
import platform

X_AUTH_TOKEN = "a371e161110b6f4c61b57a5e3e8fc6df"
BASE_URL = "https://kox947ka1a.execute-api.ap-northeast-2.amazonaws.com/prod/users"
PROBLEM = 2

def request_start_API(base_url, x_auth_token, problem_num):
    global request_cnt
    request_cnt += 1
    url = base_url+'/start'
    headers = {
        'X-Auth-Token' : x_auth_token,
        'Content-Type' : 'application/json',
    }
    data = '{ "problem" : %d }'%(problem_num)
    response = requests.post(url=url, headers=headers, data=data)
    response_json = response.json()
    auth_key = response_json["auth_key"]
    server_time = response_json["time"]
    return auth_key, server_time

def request_location_API(base_url, auth_key, problem_num):
    global request_cnt
    request_cnt += 1
    url = base_url+'/locations'
    headers = {
        'Authorization' : auth_key,
        'Content-Type' : 'application/json',
    }
    response = requests.get(url=url, headers=headers)
    response_json = response.json()
    locations = []
    if problem_num == 1:
        locations = [[0]*5 for _ in range(5)]
        for location in response_json["locations"]:
            x, y = id_to_loc(problem_num, location["id"])
            locations[x][y] = location["located_bikes_count"]
    elif problem_num == 2:
        locations = [[0]*60 for _ in range(60)]
        for location in response_json["locations"]:
            x, y = id_to_loc(problem_num, location["id"])
            locations[x][y] = location["located_bikes_count"]
    return locations

def request_trucks_API(base_url, auth_key, problem_num):
    global request_cnt
    request_cnt += 1
    url = base_url+'/trucks'
    headers = {
        'Authorization' : auth_key,
        'Content-Type' : 'application/json',
    }
    response = requests.get(url=url, headers=headers)
    response_json = response.json()
    trucks = []
    if problem_num == 1:
        trucks = [0] * 5
        for truck in response_json["trucks"]:
            trucks[truck["id"]] = truck
    elif problem_num == 2:
        trucks = [0] * 60
        for truck in response_json["trucks"]:
            trucks[truck["id"]] = truck
        
    return trucks

def request_simulate_API(base_url, auth_key, trucks_commands):
    global request_cnt
    request_cnt += 1
    url = base_url+'/simulate'
    headers = {
        'Authorization' : auth_key,
        'Content-Type' : 'application/json',
    }
    commands_json = {}
    commands_json["commands"] = trucks_commands
    data = json.dumps(commands_json)
    response = requests.put(url,headers=headers,data=data)
    response_json = response.json()
    status = response_json["status"]
    time = response_json["time"]
    return status, time

def request_score_API(base_url, auth_key):
    url = base_url+'/score'
    headers = {
        'Authorization' : auth_key,
        'Content-Type' : 'application/json',
    }
    response = requests.get(url,headers=headers)
    response_joson = response.json()
    score = response_joson["score"]
    return score

def id_to_loc(problem_num, id):
    if problem_num == 1:
        y = id // 5
        x = 4 - (id % 5)
        return x, y
    elif problem_num == 2:
        y = id // 60
        x = 59 - (id % 60)
        return x, y
    return -1, -1

def clear_console():
    system = platform.system()
    if system == "Linux" or "Darwin":
        os.system('clear')
    elif system == "Windows":
        os.system('cls')

if __name__ == "__main__":
    request_cnt = 0
    # Start API
    auth_key, server_time = request_start_API(BASE_URL, X_AUTH_TOKEN, PROBLEM)

    # Locations API
    locations = request_location_API(BASE_URL, auth_key, PROBLEM)

    # Trucks API
    trucks = request_trucks_API(BASE_URL, auth_key, PROBLEM)

    # Simulate API
    status = "ready"
    while status != "finished":
        if request_cnt > 8:
            time.sleep(1)
            request_cnt = 0
        trucks_commands = []
        n = 0
        if PROBLEM == 1:
            n = 5
        else:
            n = 10
        for i in range(n):
            temp_dict = {}
            temp_dict["truck_id"] = i
            temp_dict["command"] = [0]*10
            trucks_commands.append(temp_dict)
        status, server_time = request_simulate_API(BASE_URL, auth_key, trucks_commands)
        clear_console()
        print(server_time)
    
    # Score API
    score = request_score_API(BASE_URL, auth_key)
    clear_console()
    print(score)