# TF-1726
Second version of elo-rating bot for Russian national X-Wing league

## Docker commands
docker build -t elobot/tf-1726:0.3 .

docker run -d -it -p 8000:800 --mount type=bind,source="$(pwd)"/elo.db,target=/home/TF-1726/elo.db --mount type=bind,source="$(pwd)"/.env,target=/home/TF-1726/.env --name TF-1726 elobot/tf-1726:0.3
