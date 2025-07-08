sudo docker build --tag 'smart-lib' -f pi.Dockerfile .
sudo docker run --privileged --network host smart-lib
