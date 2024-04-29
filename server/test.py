import os

path_to_picture = os.path.join(os.getcwd(), 'images', 'client_1234_profile_picture.jpg')
print(path_to_picture)
print(os.path.isfile(path_to_picture))