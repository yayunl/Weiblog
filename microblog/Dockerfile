FROM python:3.7.7-alpine
# Create a new user
#RUN adduser -D blogowner

# Set the working directory
RUN mkdir -p /usr/code/app
WORKDIR /usr/code/

#####################################
#### Step 1: Build the environment ##
#####################################

# Copy requirements to container
COPY requirements.txt requirements.txt

# Install build dependencies, w/o cache by --no-cache
RUN apk add --virtual .build-deps gcc musl-dev libffi-dev libressl-dev python3-dev && \
#    python -m venv venv && \
    pip install --upgrade pip && \
    # Install dependencies
    pip install -r requirements.txt && \
    # Install gunicorn and pymysql driver
    pip install gunicorn pymysql
    # Remove build dependencies
#    apk del .build-deps gcc musl-dev libffi-dev libressl-dev python3-dev
#RUN    apk add libressl-dev

######################################
####  Copy files to the container ####
######################################

# Copy files from the local machine to the container
COPY app app
#COPY migrations migrations
#RUN mkdir -p /usr/app/logs
#COPY logs /usr/app/logs
COPY microblog.py startweb.sh startworker.sh ./

############################
#### Run the microblog   ###
############################

# Make bash files accessible and exectuable
RUN chmod a+x startweb.sh
RUN chmod a+x startworker.sh
# Set environment var
ENV FLASK_APP microblog.py

# Expose this port to gunicorn
EXPOSE 5000
# Start the web application with the shell script
#ENTRYPOINT ["./boot.sh"]