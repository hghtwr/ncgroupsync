from jmespath import search
from nextcloud import NextCloud
import sys
import os
from os.path import dirname
from os.path import join

sys.path.insert(0, join(dirname(__file__), 'src'))


def get_local_user_groups(dict, email):
    return [cdict for cdict in dict if cdict['email'] == email]


NEXTCLOUD_URL = os.environ['NEXTCLOUD_HOSTNAME']
NEXTCLOUD_USERNAME = os.environ.get('NEXTCLOUD_ADMIN_USER')
NEXTCLOUD_PASSWORD = os.environ.get('NEXTCLOUD_ADMIN_PASSWORD')


DRY_RUN = os.environ.get('DRY_RUN') or True
# True if you want to get response as JSON
# False if you want to get response as XML
to_js = True

nxc = NextCloud(endpoint=NEXTCLOUD_URL, user=NEXTCLOUD_USERNAME,
                password=NEXTCLOUD_PASSWORD, json_output=to_js)


# Get users

user_ids = nxc.get_users().data['users']


# Iterate over the user.
# As the API does not deliver all users on serach (missing oidc users), we load the data locally and then update them later one by one
all_user_data = []
print("Reading user information")
i = 0
for user_id in user_ids:
    print(str(i) + "/" + str(len(user_ids)), end='\r')
    all_user_data.append(nxc.get_user(user_id).data)
    i = i+1
    # We can distingiush local and central users by data.backend = user_oidc

print("Filter local and azure users")
local_users = list(
    filter(lambda user: user['backend'] != "user_oidc", all_user_data))
azure_users = list(
    filter(lambda user: user['backend'] == "user_oidc", all_user_data))

print("----- Start user conversion " + "(DRY_RUN=" + str(DRY_RUN) + ") -----")

for azure_user in azure_users:
    print(azure_user['email'])
    # print(azure_user)
    # First of all, get all the users with the same email address from the local user store
    local_users = get_local_user_groups(
        dict=local_users, email=azure_user['email'])
    # Maybe there is more than one local user with this email. Then we merge the groups together?!
    if len(local_users) > 1:
        groups = []
        for local_user in local_users:
            groups.append(local_user['groups'])
    else:
        groups = local_users[0]['groups']

    for group in groups:
        # Check if already in group, we don't want to make so many unneccassary calls
        if group not in azure_user['groups']:
            print("-- + Add " + azure_user['email'] + " to " + group)
            if not DRY_RUN:
                nxc.add_to_group(azure_user['id'], group)
        else:
            print("-- ~ User " + azure_user['email'] +
                  " already member of " + group)
# print(local_users)
# print(azure_users)
"""
    Somehow, nextcloud is not searching for email on oidc users :(
    Let's try to use the display name with like firstname.lastname to search for the users.
    "
    email = nxc.get_user(user_id).data['email']
    print("Searching all users with e-mail: " + email)
    # Search for other users with the same email...
    all_email_users = nxc.get_users(search=email, limit=100)
    print(all_email_users.data)

    # print(other_users.data)
    """
# print(all_user_data)
# print(nxc.get_user("qypqPfewiZDeyhTSM6361IIiTUn5xNUdjNTlO3_zJqs").data)


# nxc = NextCloud(endpoint=NEXTCLOUD_URL, user=NEXTCLOUD_USERNAME,
#                password=NEXTCLOUD_PASSWORD, json_output=to_js)
