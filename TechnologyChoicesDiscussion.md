# Technology Choices #



## Database ##

We have a couple of options for the type of database to use.

  * **MySQL** -- the go to option for personal projects like this. Fairly easy to set up and configure.
  * **PostgreSQL** -- Another popular open source database competing with MySQL. Known for its efficiency.
  * MariaDB -- A drop-in replacement for MySQL that is supposed to be faster.
  * SQLite -- An extremely lightweight and increasingly popular database system.
  * CouchDB -- A non-relational database designed specifically for the web.

## Framework ##

A framework is the structure that allows for server side processing of requests.

  * **PHP** -- Straight up PHP is more of the opposite of a framework. It is the easiest to get started, but extremely difficult to scale well. It is also an extremely ugly language. I (Simon) recommend against this.
  * **Ruby on Rails** -- A common web framework most famous for failing Twitter. Great community for support. I (Simon) have never used it before but I know a lot of people love it.
  * **Django** -- Feature packed Python framework. Built in administrative tools and CMS type stuff. Large community. Probably somewhat difficult to learn.
  * **Flask** -- Extremely lightweight Python micro-framework. Extremely easy to test on home computer without running Apache. I (Simon) have some experience with Flask and I really like it.

## Frontend ##

  * HTML5 -- Web standards that come built into the browser. JavaScript with new HTML5 elements, namely canvas. I think we should go with this unless we have a _really_ good reason to use something else.
  * Flash -- Has fancy vector graphics.
  * Java Applet -- Even though the code users will be writing is Java, that really doesn't give running Java client-side any advantages since all the processing will be done server-side.