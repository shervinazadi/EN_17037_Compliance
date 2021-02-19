## Docker Setup

1. Install and run [Docker Desktop](https://www.docker.com/products/docker-desktop)

2A. First time build and run the image [Running your function in a container](https://github.com/GoogleCloudPlatform/functions-framework-python/tree/master/examples/cloud_run_http)

```bash
docker build -t en17037 . && docker run --rm -p 8080:8080 -e PORT=8080 en17037
```

2B. if you already built the image, only run the image [Running your function in a container](https://github.com/GoogleCloudPlatform/functions-framework-python/tree/master/examples/cloud_run_http)

```bash
docker run --rm -p 8080:8080 -e PORT=8080 en17037
```
