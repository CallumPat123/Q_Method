# QMethodology_CITS3200

The Github Repo for Group45 of the UWA CITS3200-Professional Computing. This project is an online tool for Q Methodology

## Venv Activation

Windows : venv\Scripts\activate
Linux : source venv/bin/activate

Alternative Linux: source env/bin/activate

## Venv Deactivation

deactivate

## Pytest

to run pytest use:
python -m pytest tests
in the root dir

## Set up of local .ENV file

1. Ensure the python package python-dotenv is installed (This should be installedd by requirements.txt)
2. Create a file called '.env' in the root directory of this project
3. Copy the below code into the file
```python
#Local DB Permissions


DB_USERNAME = "postgres"
DB_PASSWORD = "123456"
DB_SERVER = "localhost"
DB_PORT = "5432"
DB_DATABASE = "qmethod"
```
4. Adjust the variables to suit your local environment.(I.e. change username and password to your local username and password.)

