import requests,math

profession_ids = {
    "Carpentry": 3,
    "Construction": 15,
    "Cooking": 13,
    "Farming": 11,
    "Fishing": 12,
    "Foraging": 14,
    "Forestry": 2,
    "Hunting": 9,
    "Leatherworking": 8,
    "Masonry": 4,
    "Merchanting": 15,
    "Mining": 5,
    "Sailing": 21,
    "Scholar": 7,
    "Slayer": 18,
    "Smithing": 6,
    "Tailoring": 10,
    "Taming": 17
}

def level_from_total_xp(total_xp):
    """
    Calculate the level based on total XP.
    """
    if type(total_xp) is not int:
        print(f"Invalid total XP type: {type(total_xp)}. Expected int.")
        return 0
    if total_xp < 0:
        print(f"Negative total XP: {total_xp}. Returning level 0.")
        return 0
    return math.floor(1+(62/(9*math.log(2)))*math.log(total_xp/6020+1))

class PlayerInformation:
    def __init__(self, username):
        self.rawdata = get_player_info(username)
        if not self.rawdata:
            raise ValueError("Invalid username or player not found.")
        self.data = self.rawdata["nodes"][1]["data"]
        
        self.reference = self.data[1]
        
        self.username = self.data[self.reference["username"]]
        self.skillmap = self.data[self.reference["skillMap"]]
        self.claims = ", ".join([self.data[self.data[x]["name"]] for x in self.data[self.reference["claims"]]])
        self.empires = ", ".join([self.data[self.data[x]["empireName"]] for x in self.data[self.reference["empireMemberships"]]])
        
        self.skillexp = {
            # Here's how the skillmap works. self.skillmap is a dictionary of 'skill #1 is item #'
            # Go to item # and you'll find a dictionary with the ID, name, title and category.
            # Go to ID - 1 and you'll find the total XP.
        }
        
        for skill_id, skill_info in self.skillmap.items():
            print(f"Skill {self.data[self.data[skill_info]["name"]]}: {self.data[self.data[int(skill_info)]["id"] - 1]}, ({skill_id,skill_info})")
            if(self.data[self.data[skill_info]["name"]] == "ANY"): continue
            self.skillexp[self.data[self.data[skill_info]["name"]]] = self.data[self.data[int(skill_info)]["id"] - 1]
            
        self.skills = {skill: level_from_total_xp(xp) for skill, xp in self.skillexp.items()}

def get_player_info(username):
    print("Fetching player info for:", username)
    # Step 1: Get the player ID from search results
    search_url = f"https://bitjita.com/players/__data.json?q={username}"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    try:
        player_data = search_data["nodes"][1]["data"]
        if str.lower(player_data[4]) != str.lower(username):
            print(f"Username {username} not found in search results.")
            return None
        player_id = player_data[3]  # index 3 = entityId
        print(f"Found player ID: {player_id}")
    except (KeyError, IndexError, TypeError):
        print("Error: Unable to extract player ID from search response.")
        return None

    # Step 2: Get the full player info using the ID
    info_url = f"https://bitjita.com/players/{player_id}/__data.json"
    info_response = requests.get(info_url)
    info_data = info_response.json()

    return info_data

def get_leaderboard(profession:str,filter=None):
    profession_id = profession_ids[profession.capitalize()]
    url = f"https://bitjita.com/skills/__data.json?sortBy={profession_id}&sortOrder=desc&page=1"
    
    response = requests.get(url)
    data = response.json()
    
    users = []
    
    for i in range(10):
        ref = data["nodes"][1]["data"][1][i]
        username = data["nodes"][1]["data"][data["nodes"][1]["data"][ref]["username"]]
        skillref = data["nodes"][1]["data"][data["nodes"][1]["data"][ref]["skills"]]
        level = data["nodes"][1]["data"][skillref[str(profession_id)]]
        
        users.append((username,level))
    
    return users

def get_empire_data(empire_name):
    search_url = f"https://bitjita.com/empires/__data.json?q={empire_name}"
    search_response = requests.get(search_url)
    search_data = search_response.json()
    
    try:
        empire_data = search_data["nodes"][1]["data"]
        if str.lower(empire_data[4]) != str.lower(empire_name):
            print(f"Empire {empire_name} not found in search results.")
            return None
        empire_id = empire_name[3]  # index 3 = entityId
        print(f"Found empire ID: {empire_id}")
    except (KeyError, IndexError, TypeError):
        print("Error: Unable to extract player ID from search response.")
        return None
    
    
    url = f"https://bitjita.com/empires/{empire_id}/__data.json"
    response = requests.get(url)
    data = response.json()
    
    if "nodes" not in data or len(data["nodes"]) < 2:
        print(f"Invalid data for empire ID {empire_id}.")
        return None
    
    empire_data = data["nodes"][1]["data"]
    
    return {
        "name": empire_data[empire_data[1]["name"]],
        "members": len(empire_data[empire_data[0]["members"]]),
        "owner": empire_data[empire_data[empire_data[empire_data[0]["members"]][0]]["playerName"]]
    }