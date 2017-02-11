export IMAGE_PREFIX = calpolypomona
export IMAGE_NAME = cv-test
export TAG = latest
export DOCKERFILE = Dockerfile-record-pi
export ARGS = 10 /root/output/output.avi
export DEVICE_MOUNT = --device=/dev/video0:/dev/video0
export VOLUME_MOUNT = -v ~/output:/root/output

build:
	docker build -t=$(IMAGE_PREFIX)/$(IMAGE_NAME):$(TAG) -f $(DOCKERFILE) .

run: remove
	eval docker run $(DEVICE_MOUNT) $(VOLUME_MOUNT) --name=$(IMAGE_NAME) $(IMAGE_PREFIX)/$(IMAGE_NAME):$(TAG) $(ARGS)

remove:
	(docker stop $(IMAGE_NAME) && docker rm $(IMAGE_NAME)) || :