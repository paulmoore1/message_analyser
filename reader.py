import os, json, csv
from os.path import join, exists, dirname, isdir
import matplotlib.pyplot as plt
from tqdm import tqdm

def get_data_dir(chat_name):
    # TODO make more robust to different data locations
    root_data_dir = join(os.getcwd(), "data")
    chat_dirs = [x for x in os.listdir(root_data_dir) if x.lower().startswith(chat_name.lower())]
    if len(chat_dirs) > 1:
        print("Multiple matches found, returning first match")
        return chat_dirs[0]
    elif len(chat_dirs) == 0:
        print("No matches found")
        return None
    else:
        print("Found chat directory...")
        return join(root_data_dir, chat_dirs[0])

# All messages in JSON are stored as message_1, message_2, etc.
def load_data(data_dir):
    json_filepaths = [join(data_dir, x) for x in os.listdir(data_dir) if x.startswith("message")]
    data_dict = None
    for filepath in json_filepaths:
        with open(filepath) as f:
            data_dict_i = json.load(f, encoding="utf-8")
        # Initialise with participants etc. all the same
        if data_dict is None:
            data_dict = data_dict_i
        else:
            # Add only the extra messages
            data_dict["messages"] = data_dict["messages"] + data_dict_i["messages"]
    return data_dict

def react_converter_dict(txt_filepath):
    convert_dict = {}
    with open(txt_filepath, "r") as f:
        lines = f.read().splitlines()
    for line in lines:
        entry = line.split()
        code = entry[0]
        value = entry[1]
        convert_dict[code] = value
    return convert_dict

# Returns all participants as a list
def get_participants(data_dict):
    participants = data_dict["participants"]
    ptcp_list = []
    for participant in participants:
        ptcp_list.append(participant["name"])
    return ptcp_list

# Does simply message counts
def count_messages(data_dict):
    messages = data_dict["messages"]
    participants = get_participants(data_dict)
    ptcp_dict = {}
    for message in messages:
        sender = message["sender_name"]
        if sender in ptcp_dict:
            ptcp_dict[sender] += 1
        else:
            ptcp_dict[sender] = 1
    return ptcp_dict

# Counts number of words in message
def count_message_length(data_dict):
    messages = data_dict["messages"]
    ptcp_dict = {}
    for message in messages:
        sender = message["sender_name"]
        if "content" in message:
            content = message["content"]
        else:
            continue
        num_words = len(content.split())
        if sender in ptcp_dict:
            ptcp_dict[sender] += num_words
        else:
            ptcp_dict[sender] = num_words
    return ptcp_dict

def count_reacts(data_dict, convert_dict):
    print("Beginning counting...")
    messages = data_dict["messages"]
    ptcp_dict = {}
    for message in messages:
        sender = message["sender_name"]
        if sender in ptcp_dict:
            ptcp_dict[sender]["total_messages"] += 1
        else:
            ptcp_dict[sender] = {"total_messages": 1}
        if "reactions" in message:
            reactions = message["reactions"]
            for entry in reactions:
                reaction = entry["reaction"]
                if reaction not in convert_dict:
                    print(reaction)
                    print(message)
                reaction = convert_dict[reaction]
                if sender in ptcp_dict:
                    # Add reaction to current total/existing reactions
                    if reaction in ptcp_dict[sender]:

                        ptcp_dict[sender][reaction] += 1
                    else:
                        ptcp_dict[sender].update({reaction: 1})
                    
                else:
                    ptcp_dict[sender].update({reaction: 1})
        else:
            continue
    #print(ptcp_dict)
    print("Finished counting...")
    return ptcp_dict


def write_react_dict(ptcp_dict, data_dir, dict_name, total_messages):
    print("Saving results...")
    root_data_dir = dirname(data_dir)
    csv_dir = join(root_data_dir, "csv_files")
    if not isdir(csv_dir):
        os.mkdir(csv_dir)
    csv_path = join(csv_dir, dict_name + ".csv")
    
    reactions = ["heart", "thumbsup", "laughing", "sad", "wow", "thumbsdown", "angry"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name"] + reactions + ["total_messages"])
        for ptcp, stats in ptcp_dict.items():
            reaction_stats = []
            for search_react in reactions:
                if search_react in stats:
                    react_count = stats[search_react]
                else:
                    react_count = 0
                reaction_stats.append(react_count)
            writer.writerow([str(ptcp)] + reaction_stats + [stats["total_messages"]])
    txt_path = join(csv_dir, dict_name + ".txt")

    with open(txt_path, "w") as f:
        f.write(str(total_messages))    


def plot_counts(counts_dict):
    plt.gca().yaxis.grid(True)
    #plt.ylim(0, 1400)
    plt.bar(range(len(counts_dict)), list(counts_dict.values()),
    align="center")
    plt.xticks(range(len(counts_dict)), list(counts_dict.keys()),
    rotation=90)
    plt.xlabel("Name")
    plt.ylabel("Message count")
    plt.tight_layout()
    plt.show()

def main():
    chat_name = "Amigos"
    data_dir = get_data_dir(chat_name)
    if data_dir is None:
        print("Couldn't find")
        return


    data_dict = load_data(data_dir)
    #convert_dict = react_converter_dict(join(os.getcwd(), "res", "emojis.txt"))
    convert_dict = {"ð\x9f\x98\x8d": "heart", "ð\x9f\x91\x8d": "thumbsup", "ð\x9f\x98\x86": "laughing",
                    "ð\x9f\x98®": "wow", "ð\x9f\x98\xa0": "angry", "ð\x9f\x98¢": "sad", "ð\x9f\x91\x8e": "thumbsdown",
                    "â\x9d¤": "heart"}
    #counts = count_messages(data_dict)
    #plot_counts(counts)
    #word_counts = count_message_length(data_dict)
    #print(word_counts)
    #plot_counts(word_counts)
    total_messages = len(data_dict["messages"])

    reacts = count_reacts(data_dict, convert_dict)
    write_react_dict(reacts, data_dir, chat_name + "-reactions",
        total_messages)

if __name__ == "__main__":
    main()