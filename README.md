# Save and Recover data from Tangle - PoC


This is a simple proof-of-concept work which deals with the following things -

- Listen for messages on specific topics from a MQTT Broker
- Save those messages in Tangle
- Retrieve these messages later from the Tangle and verify and save them to local DB
- Contains a basic visualizer (based on Flask), for viewing the data in DB


# Different parts of the project

## resources

The main resources are saved or read from this directory. Usually contains only 2 things.

- config.ini (The configuration file) : Needs to be created by user based on config_sample.ini
  - config_sample.ini mentions many fields as required in the comments, without these fields nothing would run.
  - For the optional fields, their default values are given in the ini file, they can always be changed
- values.db (The local DB where the data retrieved by verifier server will be saved, used by the visualizer)

## tangle_mqtt

The main logic for listening to topic messages, saving to tangle, running verifier server, verifying data all happens in this directory.

#### Running verifiers is completely optional. You can certainly ignore it completely.

- verifiers.py : All verifier classes need to be specified here. Basic structure of Verifier class is provided as a sample in verifiers_sample.py
  - All verifier classes need to be in this file.
  - Every class name needs to be specified in the config.ini file as class_name (check sample!)

## visualizer

A simple visualization based on Flask. By default it runs on http://localhost:9797



# Things to be careful about

- Requires python3 and some other packages as given in requirements.txt
- The globals.py in tangle_mqtt and visualizer directories needs to be same for the enclosed section. Otherwise things may break.
- config.ini needs to be created based on config_sample.ini provided before running the code
- verifiers.py file needs to be created, if wish to run verifiers.



# Running the code

- Clone the repo
- ``pip3 install -r requirements.txt``
- Create the config.ini file inside resources dir and fill it with correct configurations
- Write your verifier classes in verifiers.py (if you want verification and local saving in DB) following the sample code given
- Start verifier_server.py
- Start iota_handler.py
- Use mosquitto-clients to check if publishing and subscribing works for a topic
