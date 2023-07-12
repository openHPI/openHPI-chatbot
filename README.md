# openHPI Chatbot

## Training of the Model 

Choose the folder with the chatbot in English (openHPI_en) or in German (openHPI_de)

```sh
    rasa train
```

## Usage

### Start the Rasa Server

```sh
    rasa run
```

## Docker

In the outer project structure run:

### Docker Compose (de)

```sh
    docker-compose -f docker-compose_de.yml -p openHPI_de up --build
```

### Docker Compose (en)

```sh
    docker-compose -f docker-compose_en.yml -p openHPI_en up --build
```
