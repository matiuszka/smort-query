#!/usr/bin/env bash

if [ $# -eq 6 ]
then
    while [ $# -gt 0 ]
    do
        case $1 in
            --pyth)
                python_version=$2
                shift 2
                ;;
            --docker)
                docker_name=$2
                shift 2
                ;;
            --img)
                result_image=$2
                shift 2
                ;;
                *)
                echo "'$1' is not an option."
                echo "Use instead: --pyth, --docker or --img"
                exit
        esac
    done
else
    echo "---------------------------------------"
    echo "Run benchmark tests in docker container"
    echo "---------------------------------------"
    echo "v0.1.0, usage:"
    echo ""
    echo "$0 --pyth 3.9.0 --docker smort:v1 --img filename.png"
    exit
fi

# -------------------------------------------------------------------

build_dir="/tmp/build"
smort_dir="/home/smort"

# Check whether docker daemon is running.
docker image ls 2> /dev/null > /dev/null
if [ $? -ne 0 ]
then
  echo "Docker daemon is not running..."
  echo "Use: sudo service docker start"
  exit
fi

# Inject variables to Dockerfile template.
sed -e "s,_BUILD_DIR_,$build_dir,1" \
    -e "s,_SMORT_DIR_,$smort_dir,1" \
    -e "s,_PYTHON_VERSION_,$python_version,1" dockerfile_template > ../Dockerfile

# Build and run docker container.
docker build .. -t "$docker_name"
docker run -t "$docker_name" > /dev/null &
docker_id=$(docker ps -f "ancestor=$docker_name" --format {{.ID}})
while [ -z "$docker_id" ]
do
  docker_id=$(docker ps -f "ancestor=$docker_name" --format {{.ID}})
done
docker exec "$docker_id" python3 "$smort_dir"/benchmark/benchmark_cli.py --size 1000 3000 7000 10000 --img "$result_image"
docker cp "$docker_id":"$build_dir"/"$result_image" .
docker stop "$docker_id" > /dev/null
echo "Stopped container $docker_id"
echo ""
if [ -e "$result_image" ]
then
  echo "File '$result_image' is ready."
else
  echo "Couldn't create '$result_image' file."
fi
