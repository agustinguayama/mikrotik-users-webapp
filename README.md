# mikrotik-users-webapp
This is a Flask web interface for creating local users on Mikrotik devices.
It takes a predefined list of users, lets you type a password and connects to a predefined list of routers to apply the changes.
If the user doesn't exists on the router, it will be created. 
If the user does exists, the password will be overwritten.

Need a lot of work on error handling and customization.
