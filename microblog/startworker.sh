#!/bin/sh

rq worker -u redis://redis:6379/0 microblog-tasks --path /usr/code/
