#!/bin/bash

source .venv/bin/activate
waitress-serve --call app:run_app