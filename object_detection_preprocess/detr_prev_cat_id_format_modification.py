import os 
folder_path = "/shared/kapardi/object_detection_data/weapons_sohas/valid"

def replace_id_with_custom_id(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            # file.write(line.replace("0", "3", 1))  # Replace only the first occurrence per line
            # file.write(line.replace("1", "30", 1))  # Replace only the first occurrence per line
            # file.write(line.replace("2", "5", 1))  # Replace only the first occurrence per line
            # file.write(line.replace("3", "31", 1))  # Replace only the first occurrence per line
            # file.write(line.replace("4", "32", 1))  # Replace only the first occurrence per line
            file.write(line.replace("5", "33", 1))  # Replace only the first occurrence per line


for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        replace_id_with_custom_id(os.path.join(folder_path, filename))

print("All files processed.")