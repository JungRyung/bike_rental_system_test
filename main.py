import requests
import json
import time
import os
import platform

X_AUTH_TOKEN = "20de00fa389a048b7f5b1b5a80b8b85d"
BASE_URL = "https://kox947ka1a.execute-api.ap-northeast-2.amazonaws.com/prod/users"
PROBLEM = 1

class Truck:
    def __init__(self, problem_num, location_id, loaded_bikes_count):
        self.__location_id = location_id
        self.__location_loc = id_to_loc(problem_num, location_id)
        self.__loaded_bikes_count = loaded_bikes_count
        self.__status = "ready"
        self.__destination_loc = (0,0)
        self.__remained_commands = []

    def update(self, problem_num, location_id, loaded_bikes_count):
        self.__location_id = location_id
        self.__location_loc = id_to_loc(problem_num, location_id)
        self.__loaded_bikes_count = loaded_bikes_count

    def __search_route(self, currrent_loc, destination_loc):
        commands = []
        cx, cy = currrent_loc
        nx, ny = destination_loc
        dx = nx - cx
        dy = ny - cy
        if dx > 0:      # 아래로 이동
            for _ in range(dx):
                commands.append(3)
        elif dx < 0:    # 위로 이동
            for _ in range(-dx):
                commands.append(1)
        if dy > 0:      # 오른쪽으로 이동
            for _ in range(dy):
                commands.append(2)
        elif dy < 0:    # 왼쪽으로 이동
            for _ in range(-dy):
                commands.append(4)
        return commands

    def set_location_id(self, id):
        self.__location_id = id
        
    def operate(self, over_located_locs, under_located_locs):
        commands = []
        
        x, y = id_to_loc(self.__location_id)
        self.__location_loc = (x,y)
        
        # 트럭이 아무것도 안하고 있고 가지고 있는 자전거가 한대도 없을 때 -> 자전거를 상차하기 위한 장소를 검색 후 이동
        if self.__status == "ready" and  self.__loaded_bikes_count == 0:
            if over_located_locs:
                self.__destination_loc = over_located_locs.pop()
                tmp_commands = self.__search_route(self.__location_loc, self.__destination_loc)
                tmp_commands.append(5)
                while len(commands) < 10:
                    commands.append(tmp_commands.pop(0))
                if len(tmp_commands) > 0:
                    self.__remained_commands = tmp_commands
                    self.__status = "tasking"
        # 트럭이 아무것도 안하고 있고 가지고 있는 자전거가 있을 때 -> 자전거를 하차하기 위한 장소를 검색 후 이동
        elif self.__status == "ready" and self.__loaded_bikes_count > 0:
            if under_located_locs:
                self.__destination_loc = under_located_locs.pop()
                tmp_commands = self.__search_route(self.__location_loc, self.__destination_loc)
                tmp_commands.append(6)
                while len(commands) < 10:
                    commands.append(tmp_commands.pop(0))
                if len(tmp_commands) > 0:
                    self.__remained_commands = tmp_commands
                    self.__status = "tasking"
        # 트럭이 작업중인 경우 남은 작업을 마무리
        elif self.__status == "tasking":
            for command in self.remained_commands:
                commands.append(command)
            if len(commands) < 10:
                n = 10 - len(commands)
                for _ in range(n):
                    commands.append(0)
            self.__remained_commands = []
            self.__status = "ready"
            return commands

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
    over_located_locs = []
    under_located_locs = []
    if problem_num == 1:
        locations = [[0]*5 for _ in range(5)]
        for location in response_json["locations"]:
            x, y = id_to_loc(problem_num, location["id"])
            locations[x][y] = location["located_bikes_count"]
            if locations[x][y] > 4:
                over_located_locs.append((x,y))
            if locations[x][y] < 4:
                under_located_locs.append((x,y))
    elif problem_num == 2:
        locations = [[0]*60 for _ in range(60)]
        for location in response_json["locations"]:
            x, y = id_to_loc(problem_num, location["id"])
            locations[x][y] = location["located_bikes_count"]
            if locations[x][y] > 3:
                over_located_locs.append((x,y))
            if locations[x][y] < 3:
                under_located_locs.append((x,y))
    return locations, over_located_locs, under_located_locs

def request_trucks_API_init(base_url, auth_key, problem_num):
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
            trucks[truck["id"]] = Truck(problem_num, truck["location_id"], truck["loaded_bikes_count"])
    elif problem_num == 2:
        trucks = [0] * 60
        for truck in response_json["trucks"]:
            trucks[truck["id"]] = Truck(problem_num, truck["location_id"], truck["loaded_bikes_count"])
    return trucks

def request_trucks_API_update(base_url, auth_key, problem_num):
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
        return (x, y)
    elif problem_num == 2:
        y = id // 60
        x = 59 - (id % 60)
        return (x, y)
    return (-1, -1)

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
    locations, over_located_locs, under_located_locs = request_location_API(BASE_URL, auth_key, PROBLEM)

    # Trucks API
    trucks = request_trucks_API_init(BASE_URL, auth_key, PROBLEM)

    # Simulate API
    status = "ready"
    while status != "finished":
        if request_cnt > 8:
            time.sleep(1)
            request_cnt = 0

        # locations 업데이트 -> 바이크가 충분한 곳과 부족한 곳 판단
        locations, over_located_locs, under_located_locs = request_location_API(BASE_URL, auth_key, PROBLEM)

        # 트럭 상태 업데이트
        trucks_info = request_trucks_API_update(BASE_URL, auth_key, PROBLEM)
        for truck_info in trucks_info:
            trucks[truck_info["id"]].update(PROBLEM, truck_info["location_id"], truck_info["loaded_bikes_count"])

        # 트럭 operate
        

        # 트럭 명령 리스트 생성
        trucks_commands = []
        n = 0
        if PROBLEM == 1:
            n = 5
        else:
            n = 10
        for i in range(n):
            temp_dict = {}
            temp_dict["truck_id"] = i
            temp_dict["command"] = trucks[i].operate()
            trucks_commands.append(temp_dict)

        # 시뮬레이션
        status, server_time = request_simulate_API(BASE_URL, auth_key, trucks_commands)
        clear_console()
        print(server_time)
    
    # Score API
    score = request_score_API(BASE_URL, auth_key)
    clear_console()
    print(score)