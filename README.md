# Torch Exercise

- **Exercise:** Create a modified interface to the NYC Subway status dashboard available online, with history information and the rudiments of a basic alerting feature.

## Web Service Overview

**Note:** A line is considered delayed if the status is equal to "Delays", and is considered not to be delayed if it has any other status (assumes all statuses are other than "Delays" are equivalent).

**The Web Service does the following things:**

1. Continuously monitors the status of MTA service to see whether a line is delayed or not.
1. When a line transitions from not delayed -> delayed, prints the following message to console: `Line <line_name> is experiencing delays`
1. When a line transitions from delayed - not delayed, prints the following message to console: `Line <line_name> is now recovered`
1. Exposes an endpoint called `/status`, which takes the name of a particular line as an argument and returns whether or not the line is currently delayed.
1. Exposes an endpoint called `/uptime`, which also takes the name of a particular line as an argument and returns the fraction of time that hs not been delayed since inception. "uptime" is defined as `1 - (total_time_delayed / total_time)`

## Setup

Requirements

- Python-3.7
- pip3

cd into the app directory and create virtualenv

```
pip3 install virtualenv
virtualenv venv --python=python3
source venv/bin/activate
```

Install dependencies

```
pip3 install -r requirements.txt
```
From the app directory run:
```
python app.py
```
To test run pytest as a module from the app directory:
```
python -m pytest test
```

## API Documentation
- **Available Lines:** "123", "456", "7", "ACE", "BDFM", "G", "JZ", "L", "NQR", "S", "SIR"

### Status
Send a `GET` request to `v1/status/<string:line>` endpoint (where `line` = name of a particular line).
See list of 'Available Services' above.  An example response for a line without delays would be:
```
{
    isDelayed: false
}
```
If the line is delayed, this would be true.

### Uptime
Send a `GET` request to `v1/uptime/<string:line>` endpoint (where `line` = name of a particular line).
See list of 'Available Services' above.  An example response for a line with 100% uptime would be:
```
{
    uptime: 1
}
```
If the line is delayed, this would be true.

### Errors
If requests are invalid, the API will respond with a list of errors in the following format:
```
{
    errors: [
        {
            status: 400,
            detail: "Line does not exist"
        }
    ]
}
```
