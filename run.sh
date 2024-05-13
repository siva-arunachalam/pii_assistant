docker kill mask
sleep 1

docker run \
  --rm \
  --detach \
  --env-file .env \
  --volume ~/work/pii_assistant:/usr/src/app \
  --publish 8503:8503 \
  --workdir /usr/src/app \
  --name mask \
  siva:assist mask_ui.py --server.port 8503
