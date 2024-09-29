# Testing `dhdt.py` using `default.ini`

## Steps

- Open TWCC
- Create a development container using the `Custom Image` 
- In the image, select `tensorflow-23.11-tf2-py3:AChydro002` and create the container
- Open VS Code and connect to the container using SSH
- Navigate to the `CARST/examples/dhdt` folder
- Run `dhdt.py default.ini`

## Bug Encountered

When the path is not confirmed correctly or a typo occurs, the system doesn't notify that the file is missing but directly displays an error.
