import os, json
from os.path import join, exists

def get_data_dir(chat_name):
    # TODO make more robust to different data locations
    root_data_dir = join(os.getcwd(), "data")
    chat_dirs = [x for x in os.listdir(root_data_dir) if x.lower().startswith(chat_name)]
    if len(chat_dirs) > 1:
        print("Multiple matches found, returning first match")
        return chat_dirs[0]
    elif len(chat_dirs) == 0:
        print("No matches found")
        return None
    else:
        return join(root_data_dir, chat_dirs[0])

# All messages in JSON are stored as message_1, message_2, etc.
def load_data(data_dir):
    json_filepaths = [join(data_dir, x) for x in os.listdir(data_dir) if x.startswith("message")]
    data_dict = None
    for filepath in json_filepaths:
        with open(filepath) as f:
            data_dict_i = json.load(f)
        # Initialise with participants etc. all the same
        if data_dict is None:
            data_dict = data_dict_i
        else:
            # Add only the extra messages
            data_dict["messages"] = data_dict["messages"] + data_dict_i["messages"]
    return data_dict


def main():
    chat_name = "whoneedsfriendswhenyouhavejesus"
    data_dir = get_data_dir(chat_name)
    data_dict = load_data(data_dir)

if __name__ == "__main__":
    main()