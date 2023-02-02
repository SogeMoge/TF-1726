# TF-1726
Second version of elo-rating bot for Russian national X-Wing league

## Prepare VM
sudo apt-get update && sudo apt=get -y upgrade && sudo apt-get -y install podman git
sudo apt-get -y install python3-pip && pip3 install podman-compose
podman login docker.io
touch elo.db && touch .env

## Prepare Systemd


## Docker commands
docker build -t elobot/tf-1726:0.3 .
### start container mith mounted db and env
docker run -d -it -p 8000:800 --mount type=bind,source="$(pwd)"/elo.db,target=/home/TF-1726/elo.db --mount type=bind,source="$(pwd)"/.env,target=/home/TF-1726/.env --name TF-1726 elobot/tf-1726:0.3
