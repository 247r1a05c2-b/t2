from collections import defaultdict
_events=defaultdict(list)

def add_many(events):
    for e in events: _events[e.incident_id].append(e)

def get(incident_id): return list(_events.get(incident_id,[]))
def incidents(): return list(_events.keys())
def clear(): _events.clear()
