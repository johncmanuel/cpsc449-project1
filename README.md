# cpsc449-project1

Project 1 for CPSC 449: Backend Engineering

Team:

1. Tomas Oh
2. Jahn Tibayan
3. Nestor Reategui
4. John Carlo Manuel (CWID: 884779844)

## How to Run

1. Install the latest versions of Python and PostgreSQL. This can be done either manually through official websites or easily with Devbox.
2. Setup a virtual environment and activate it. If using Devbox, the virtual environment is already setup and activated upon launch.
3. Install the required packages using `pip install -r requirements.txt`
4. Setup the PostgreSQL database and create and modify a `.env` file accordingly to `.env.example`.
5. Start the database server and run the Flask server, `python main.py`

## Project Overview

This project contains two components: a movie ratings service and a file upload API.

### Movie Ratings Service

The movie ratings service is an API that allows users to interact with a database of movies and ratings. Users can add, update, delete, and retrieve movies and ratings. Admins are not allowed to rate movies but they can add new movies and delete any movie's user rating.

Users are able to create an account with a username and password. Then, they are able to login and perform the aforementioned operations. Admins are able to login at the same endpoint.

### File Upload API

The File Upload API enables users to upload files of their choice through a POST request. The supported extensions are:

1. .txt
2. .pdf
3. .png,
4. .jpg,
5. .jpeg,
6. .gif
