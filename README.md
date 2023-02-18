# Nextcloud Group Synch
A simple script that will help migration of nextcloud users to a central identity provider. It will search for users with same email address and then replicate the group assignments.

Today, central user management is key. Nextcloud supports OIDC Identity Provider. If you want to switch from local nextcloud users to centrally managemed users by OIDC you wwill also have to migrate the user group assignments. 
This tool will automatically search for users with the same email address and replicate the group assignments between them.

