# Battle Critters #

Battle Critters is a website that allows users to write AI code to control critters which compete in a battle.



## Frontend ##

HTML, CSS and JavaScript stuff. The code that gets sent to the client.

### Game Viewer Page ###

Loads data from the game retrieval system and displays it. Allows viewer to watch battle like a movie or one frame at a time. Shows number of critters for each class as well as the frame number.

### Editor Page ###

Displays a text editor allowing a user to edit code they are the author of. Text is automatically saved.
  * Text Editor -- [hrrp://codemirror.net CodeMirror]
  * Auto-Save
  * Validate Button
  * Test Button
  * Publish ?

### Dashboard ###

The main page displayed when a user logs in.
  * List of written AIs with statistics
  * Create new AI
  * Statistics

### Static(ish) Info Pages ###

Pages that don't really change based on current user.
  * Home Page
  * Privacy Policy
  * About Us
  * FAQ

## Backend ##

The hard stuff that runs on the server.

### Game Simulator ###

Runs a battle and writes the output to a file.

### Game Storage/Retrieval ###

Sends the data from a completed game to the client. Might be split up into different chunks of data or some more complicated system so that playback can begin before

### Code Validation ###

Checks a code file to see if it compiles. Also does many security checks.

### Code Storage ###

Saves code and metadata in a database.

**Database Fields**
  * Code ID : int
  * Code Title : varchar(256)
  * Actual Code : text
  * Author ID : int, link to User table
  * last edited : timestamp
  * last validated : timestamp

### Class Storage ###

While we can easily store the .java files in a database, we probably need to store the .class files on the file system. This would allow for easier dynamic class loading. I think each use should have a folder that corresponds to each user, all in a subfolder of the game.class file. This way, the main Game class can easily dynamically load the others using
```
Class UserCritter = Class.forName("username.classname");
```

When we store the code, we need to add the proper package at the top of the file.

### Ranking System ###

This will be more complicated than we were first thinking.

### User Data ###

Create, store and retrieve user login information.

**User table fields**
  * ID : int
  * username : varchar(256)
  * passwordHash : varchar(256)

### Security ###

All the things we have to do to prevent malicious code being executed on the server.
  * Sanitize code for database insertion
  * Limit Run time and memory usage
  * Only allow java.lang. and subpackages