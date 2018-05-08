# nginx-rtmp-auth
Backend for handling nginx rtmp module stream authentication

Note: This is still a work in progress at of 2018/05/06.  Working through the bugs to integrate this into a docker container.

# Python/Flask
Requirements:
  - Nginx with RTMP module (https://github.com/arut/nginx-rtmp-module)
  - a PostgreSQL server
  - Flask, Flask API
  - psycopg2

Server-side configuration:
  - Set nginx.conf as the live nginx conf (location of file depends on system)
  - Set the web root to an appropriate value
  - Set worker_processes to 1 to work around an issue in the nginx-rtmp module
  - Set the name of the rtmp server application block to whatever is desired (defaults to "stream")
  - Adjust the on_publish directive URL to reflect where the auth script is being served from (e.g. with the Flask development server, the URL would be http://localhost:5000/auth)
  - Set PostgreSQL-related variables in config.py (host, username, password, database, usertablename)
  - Ensure the PostgreSQL server is accepting connections from the user specified in common.py and the user specified in common.py has the correct privileges to read from the defined users table
  - Configure the users table
    - The following schema are expected (but easily changed):
      - username VARCHAR(64)
      - email VARCHAR(64)
      - password VARCHAR(64)
      - idhash VARCHAR(64)
      - app varchar(128) NOT NULL default 'live,'
      - all_access int NOT NULL default 0
      - enabled int NOT NULL default 1
      - date_added timestamp default NOW()
      <p>Table Create SQL:
      <code>
       CREATE TABLE user_store (
            username varchar(64) primary key,
            email varchar(128),
            password varchar(64),
            idhash varchar(64) NOT NULL,
            app_stream varchar(1024),
            streams SMALLINT NOT NULL default 0,
            enabled int NOT NULL default 1,
            date_added timestamp default NOW(),
            CHECK (streams >= 0),
            CHECK (streams <= 99),
            CHECK (enabled >= 0),
            CHECK (enabled <= 1)
        );
      </code>
      <p>Example User SQL (basic, single channel):
      <code>
       Insert into user_store (username, idhash, app_stream) VALUES ('example', 'example', 'live/example');
      </code>
      <p>Example User SQL (single app, unlimited channels):
      <code>
       Insert into user_store (username, idhash, app_stream) VALUES ('unlimited', 'example', 'live/*');
      </code>
    - Other columns may be added as required

# Non-specific

Broadcaster-side configuration (assuming OBS):
  - Under Broadcast Settings, set Custom as the streaming service
  - Set server to "rtmp://domain.example:1935/APP/STREAM?user=USERNAME&id=IDHASH"
  - Set play path to stream
  
Player-side configuration:
  - The RTMP URL will be in the format "rtmp://domain.example:1935/APP/STREAM" (assumes default rtmp server application block name of "stream")

Known issues:
  - OBS Studio (aka OBS MultiPlatform aka OBS Linux/Mac) versions <0.11.4 mangle variables defined in the server/stream URL when passing them to nginx, meaning that information sent that way (i.e. idhash) cannot be accessed by the authentication script
