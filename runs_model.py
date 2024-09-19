import json
from operator import attrgetter
import time
from threading import Thread
from random import random
import re

# ========================================================
# Run Model
# ========================================================
PAGE_SIZE = 100

class Run:
    # mock runs database
    db = {}

    # from typing import Optional

    # def __init__(self, id_: Optional[int] = None, distance: Optional[float] = None, duration: Optional[str] = None, timestamp: Optional[str] = None):
    def __init__(self, id_=None, distance=None, duration=None, timestamp=None):
        self.id = id_
        self.distance = distance  # in kilometers
        self.duration = duration   # in minutes
        self.timestamp = timestamp  # date of the run
        self.errors = {}

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def update(self, distance, duration, timestamp):
        self.distance = distance
        self.duration = duration
        self.timestamp = timestamp

    def validate(self):
        self.errors = {}  # Reset errors

        if not self.distance:
            self.errors['distance'] = "Distance is required."

        # Check duration format HH:MM:SS or MM:SS
        if self.duration is None:
            self.errors['duration'] = "Duration is required."
        elif re.match(r'^\d{1,2}:\d{2}:\d{2}$', self.duration):
            # Valid HH:MM:SS
            pass
        elif re.match(r'^\d{1,2}:\d{2}$', self.duration):
            # Valid MM:SS, will prepend '00:'
            self.duration = '00:' + self.duration
        else:
            self.errors['duration'] = "Duration must be in HH:MM:SS or MM:SS format."

        if self.timestamp is None:
            self.errors['timestamp'] = "Timestamp Required"

        return len(self.errors) == 0  # Return True if no errors


    def save(self):
        if not self.validate():
            return False

        # Assign a new ID if it's a new run
        if self.id is None:
            max_id = max((run.id for run in Run.db.values()), default=0)  # Get max ID or 0 if db is empty
            self.id = max_id + 1

        Run.db[self.id] = self  # Save the Run instance to the database
        Run.save_db()  # Save to the JSON file
        return True


    def delete(self):
        if self.id in Run.db:
            del Run.db[self.id]
            Run.save_db()


    @classmethod
    def count(cls):
        time.sleep(2)
        return len(cls.db)

    @classmethod
    def all(cls, page=1):
        page = int(page)  # Convert the page number to an integer
        start = (page - 1) * PAGE_SIZE  # Calculate the start index for pagination
        end = start + PAGE_SIZE  # Calculate the end index for pagination
        return list(cls.db.values())[start:end]  # Return the slice of runs for the requested page

    @classmethod
    def search(cls, text):
        result = []  # Initialize an empty list to store matching runs
        for run in cls.db.values():  # Iterate over all runs in the database
            match_distance = run.distance is not None and text in str(run.distance)
            match_duration = run.duration is not None and text in str(run.duration)
            match_timestamp = run.timestamp is not None and text in str(run.timestamp)

            if match_distance or match_duration or match_timestamp:  # If any match, add to results
                result.append(run)  # Append the matching run to the result list
        return result  # Return the list of matching runs

    # @classmethod
    # def search(cls, text):
    #     result = []  # Initialize an empty list to store matching runs
    #     for run in cls.db.values():  # Iterate over all runs in the database
    #         match_duration = run.duration is not None and text in str(run.duration)
    #         match_timestamp = run.timestamp is not None and text in str(run.timestamp)
    #         if match_duration or match_timestamp:  # If any match, add to results
    #             result.append(run)  # Append the matching run to the result list
    #     return result  # Return the list of matching runs


    @classmethod
    def load_db(cls):
        with open('runs.json', 'r') as runs_file:
            runs = json.load(runs_file)  # Load runs data from JSON file
            cls.db.clear()  # Clear the existing database
            for run_data in runs:
                cls.db[run_data['id']] = Run(run_data['id'], run_data['distance'], run_data['duration'], run_data['timestamp'])


    @staticmethod
    def save_db():
        out_arr = [run.__dict__ for run in Run.db.values()]  # Prepare data for JSON serialization
        with open("runs.json", "w") as f:
            json.dump(out_arr, f, indent=2)  # Write to runs.json with pretty formatting

    @classmethod
    def find(cls, id_):
        id_ = int(id_)
        run = cls.db.get(id_)  # Retrieve the Run object by its ID
        if run is not None:
            run.errors = {}  # Clear any existing errors

        return run  # Return the found Run object or None


class Archiver:
    archive_status = "Waiting"
    archive_progress = 0
    thread = None

    def status(self):
        return Archiver.archive_status

    def progress(self):
        return Archiver.archive_progress

    def run(self):
        if Archiver.archive_status == "Waiting":
            Archiver.archive_status = "Running"
            Archiver.archive_progress = 0
            Archiver.thread = Thread(target=self.run_impl)
            Archiver.thread.start()

    def run_impl(self):
        for i in range(10):
            time.sleep(1 * random())
            if Archiver.archive_status != "Running":
                return
            Archiver.archive_progress = (i + 1) / 10
            print("Here... " + str(Archiver.archive_progress))
        time.sleep(1)
        if Archiver.archive_status != "Running":
            return
        Archiver.archive_status = "Complete"

    def archive_file(self):
        return 'runs.json'

    def reset(self):
        Archiver.archive_status = "Waiting"

    @classmethod
    def get(cls):
        return Archiver()
