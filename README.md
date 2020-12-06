# Calendars to Notion Synchronization

This script utilizes the unofficial [Notion API](https://github.com/jamalex/notion-py) to get calendar eventso from external sources to a Notion Collection database of Calendar events. 
To integrate with others calenders, the apis used are:
- [Google Calendar API](https://developers.google.com/calendar)
- Microsoft Outlook: To Do

Want to extend to other email services? 
You just need to implement a class extending the `src.repositories.ICalendar` interface, and create a new type pattern match to instatiate that class.

PR's are welcomed!

## Where can I run the script?

This script can run in any machine running python. 
You can run it in you computer, and run it every now and then. Or you can put it running as a chron job in any host - A cloud one, or your always-on mini computer at home.
Want to run this as a lambda function on a free cloud account? Go ahead!

In this documentation, I only explain how to run this on a linux host.
Any Pull Request aim to improve the coverage on how to install in other endpoits are welcome!

## How does this work?

This script works by defining calendars (e.g. the "main" Google Calendar, the vacation Google Calendar, the Work Google Calendar, the Notion Calendar, etc) and by defining synchronization flows - saying that Work Google Calendar should sync to Notion, or that Main Google Calendar should sync to Notion.
You can define as many flows as you want.

## Defining Calendars

### Defining the schema integration

In every integration, we need to map values. This is, the events in every calendar does not necessarely have the same set of attributes, but we can map this.
This script uses the following internal attributes of a calendar event:
- id: the id of the event
- name: the name of the event
- url: the url of the event
- start: the start date of the event
- end: the end date of the event
- organizer: the email of the organizer
- status: a string representing if event is confirmed, maybe or not going
- owner: a string identifying the owner calendar of the event


In each calendar definition, we need to map these internal attributes with the attributes of the event calendar attribute's service.

### Google Calendar

#### Pre Requisites

You need to create a google project, activate the Google Calendar API in that project and create a service account.
You can find instructions for these in [here](https://support.google.com/a/answer/7378726?hl=en).
By the end of this, you should have a json file with the credentials of the service account.

#### Configurations

- type: the value should be "googlecalendar" (or any upper/lower case variation, the script will put this value in lowercase)
- credentials_file_path: the file for the app service credentials
- scopes: the scope list. This should be `https://www.googleapis.com/auth/calendar`
- calendar_id: this should be the id of the target calendar. You can check this in Google Calendar
- schema:
      id: id
      name: summary
      url: htmlLink
      start: start
      end: end
      organizer:
        - nested:
            - organizer
            - email
      status: Status
      owner:
        - constant: $calendar_id

### Notion Calendar

#### Pre Requisites

##### Notion Collection

Create a collection with at least columns for these semantincs:

- A string Id column, e.g. Id
- A string Name column, e.g. Name
- An URL column, e.g. url
- A date Start date column, e.g. Start Date
- A date End date column, e.g. End Date
- A string Organizer column, e.g. Organizer
- A string Status column, e.g. Status
- A string Owner column, e.g. Owner

When you refer these in the configuration, they should be in lower case and with underscore instead of a space.
If you choose a column name to be "Id", then this is a special case. Given that notion elements have an attribute `id` already.
In this case, this "Id" should be refered in the schema as it is defined and never in lower case, because the `id` already exists.

##### Notion Token

Open the notion workspace for the calendar you want to sync in your browser. Open the developer console using `Inspect`. Tab over to `Application` and select the `Cookies` sub-menu. Look for the cookie named `token_v2` and copy its value.

##### Notion Collection URL

Navigate to the notion calendar you want to sync and copy the link.
Note that this is the collection / database url, and not the page where the collection is.


#### Configurations

- type: this value should be `notioncalendar`
- notion_token: a string with the token
- notion_calendar_url: a string with the calendar url
- schema:
      id: Id
      name: name
      url: url
      start:
        - nested:
          - start_date
          - start
      end:
        - nested:
          - end_date
          - start
      organizer: organizer
      status: status
      owner: owner

## Defining Sync Flows

A sync flow is a named entity that contains:
- The calendar from where I am getting the events
- The calendar to where I am pushing the events
- The time window that I am using.

An example of a sync flow named `GoogleCalendar2Notion` would be:

```
GoogleCalendar2Notion:
sync_from:
    Main_Calendar
sync_to:
    Notion_Calendar
sync_time:
    days: 60
```

## How to set this up?

1. Clone the repository
2. Create a virtualenv with python >=3.5

    - `python -m venv venv`
3. Install the requirements in the virtualenv

    - `venv/bin/python -m pip install -r requirements.txt`
4. Set your `conf/config.yaml` file. You can find an example file in `conf/config_example.yaml.`
5. Run your script

    - `venv/bin/python main.py --config-file conf/config.yaml`
6. Wait for it to complete

