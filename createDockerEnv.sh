sudo docker build --tag 'room-pi' -f pi.Dockerfile .
sudo docker run --privileged --network host room-pi
