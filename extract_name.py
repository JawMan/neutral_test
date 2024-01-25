import os


def extract_subdirectory_names(directory_path):
    subdirectory_names = []
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            subdirectory_names.append(item)
    return subdirectory_names



#parent_directory1 = '/Users/jmehrabanian/Library/Mobile Documents/com~apple~CloudDocs/MEMES/neutral_memes'
#subdirectory_names = extract_subdirectory_names(parent_directory1)
#print(subdirectory_names)


def extract_file_names(directory_path, extensions):
    file_names = []
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path) and any(item.endswith(ext) for ext in extensions):
            file_names.append(item)
    return file_names


parent_directory2 = '/Users/jawman/IdeaProjects/neutral_test/jm_memes/Dataset1'
extensions = ['.jpg', '.jpeg', '.png']
file_names = extract_file_names(parent_directory2, extensions)
print(file_names)
