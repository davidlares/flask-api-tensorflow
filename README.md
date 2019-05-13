# davidFlaskRestful

This repo contains exercises for RestFul API's using Flask MicroFramework, Docker Compose, MongoDB and the Tensorflow Inception API v3 for image recognition.

Each API uses the same MongoDB Database (local environment) with shared collections. For this examples we only use POST verbs for handling basic actions such as updating collections and inserting documents.

## Endpoints

If I explain every single endpoint of each project, this will take a long time.

Please check the `add_resource` method of each example to know the endpoints available.

## Exercises

  1. The first one `arithmetic.py` is a simple API for returning basic arithmetic operations (addition, subtraction, multiplication and division) using the HTTP Interface.

  2. The second one `user-auth-token.py` simulates an authentication method with email and password credentials for storing words or sentences in the databases with a token assignations for "restrictions" or "payments" for using the API's

  The authentication passwords are hashed and encrypted using the `bcrypt` python library.

  3. `similarity.py` uses the `spacy` Library for handling **NLP (Natural Language Processing)** on strings for getting the certainly rate if are the same or not. (We call it: ratio rate)

  Ratio is a number range between 0 and 1. If it's closer to 1, it's more close in similarity.

  4. the `image-classification.py` file use a full `.jpg` url path to validate with the recognition API and detect which object or something matches with the image content.

  The `classify_image.py` file is the model file which contains the whole logic and functionality from Google's Tensorflow, the `image-classification.py` file use it for threading the matching operations

  5. and lastly, the `bank.py` which simulates simple bank operations, like adding money to account, balance, loans and more things related.


## Libraries used

There's a lot of them but the main one is the `flask_restful` and of course the Flask

You also can refer to the `requirements.txt` to check the framework version used and other dependencies required. (file listed on the `web` folder) for container provisioning.

## Usage

The full setup could be done with Docker Compose service, please refer to the `docker-compose.yaml` file on the root location to see which services are running.

Each module (or folder) will represent a layer in the full stack setup

`docker-compose build` for setting up and provisioning the container environments

`docker-compose run` running the Docker services.

The `app.py` is the main script of the project, you can replace the content for any example to it and will be ready to work.


## Credits

- [David Lares S](https;//twitter.com/davidlares3)

## License

- [MIT](https://opensource.org/licenses/MIT)
