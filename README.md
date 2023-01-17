# Star_wars_characters
Star Wars characters explorer is a simple application allowing you to fetch collections containing all of the saga's characters.
The data is provided by the SWAPI, you can visit at https://swapi.dev/.

# Libraries
The app was written using Python version 3.10 and the following libraries
- Django 4.1.3
- petl 1.7.12
- requests 2.25.1

App also uses boostrap v5.3.0-alpha1

# Running the app 
### Docker
To run in docker container first build container and run it with the following commands

    docker build . -t docker-star-wars-characters
    docker run -p 8000:8000 docker-star-wars-characters
    

This method is the easiest but since there is only simple Dockerfile, collections will not persist between container stops.

### Locally
To run locally on your machine first it is recommended you create Python virtual environment with Python 3.10. Then from projects home folder run

    pip install -r requirements.txt
	cd star_wars_project
	python manage.py runserver
	

# Possible future updates
- **Adding tests** - tests are required for any application, as they are the base for future growth and stability
- **Table transformations with Multi Processing** - API scraping is done with usage of multi threading but for larger datasets multiprocessing would allow to process scraped data faster
- **Adding docker compose** - better docker container would allow for application state to persist
