# cpsc449-project1

Project 1 for CPSC 449: Backend Engineering

Team: Tomas Oh, Jahn Tibayan, Nestor Reategui, John Carlo Manuel

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

