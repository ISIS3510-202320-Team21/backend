# Backend instructions

Run the following commands to install the required libraries:

```
pip install fastapi
pip install "uvicorn[standard]"
pip install SQLAlchemy
pip install databases
```

You will also need postgres running on the background for the app to work. If you want to adjust the code to run on other database you can edit the database.py file.

The postgres database name for default is sportpal_db, the username is postgres and the password 1234. To create the database you can do this:

```
psql -U postgres
postgres# CREATE DATABASE sportpal_db OWNER postgres;
postgres# ALTER USER postgres WITH PASSWORD '1234';
```

To launche the app go to the root folder and use:

```
uvicorn main:app --reload
```
