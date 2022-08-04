# **Election System Project**

## Overview
---

I spearheaded this project along with two other fellow students in the creation of this election system. The main objective if this
project was to create an election system that allowed users to create elections and to have other users register and vote in these
elections. The project is a web application that is based in `Python`. It uses `Flask` as its web application framework due to its 
built-in development server as well as the fast debugger provided. `HTML` is utilized for the web page creation. Laslty `MYSQL` was used
for the database for its scalability, flexibility, and management ease.


## How to install

---

1) To use this you will first need to download all files as a zip file and unpack it or pull it to github desktop
2) Next you will need to install MYSQL using `brew install mysql`
3) Then you will need to setup a virtual enviroment
   1) Run the following commands
      1) `pip install virtualenv`
      2) `cd project_folder`
      3) `virtualenv venv`
      4) `source venv/bin/activate`
4) Then you need to change the username and password in `mysqldborm.py`
5) After that you will need to run `pip install pipreqs` in the terminal
6) Following that, run `pip install -r requirements.txt` in the terminal
7) Then run `create_tables.py`
8) Finally run `python app.py` and click on the link provided in the terminal to open the app

## How to use

---

There are 3 different kinds of users you can create
1) The voter - this user can vote in elections and see the results of their election
2) The Admin - this user can set up elections and approve accounts
3) The Polling manager - this user can approve and end elections

You can register any type of user, but please note that an admin should be created first, then a polling manager,
followed lastly by a voter just so the accounst can all be approved in order.

From there you can create an election as an admin, and set the polling manager. After that your voter can vote for the
election you created and then the polling manager can end it once all votes have been cast!

## Credits

---

This project was only possible due to the contributions of my fellow groupmates:
- Sebastion Rivera - Login Design
- Steve - Front-End design and helped with the database
- Myself - Full-stack for the project

(Note: Not many commits due to being copied over from my local files)

## License

---

MIT License

Copyright (c) 2022 Ben DeSollar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



