import pytest
from src.event import EventHandler, Event




def test_get_events_empty_month():
    EventHandler.reset_events()  # Reset events dictionary
    test_month = 7
    
    result = EventHandler.get_events(test_month)
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_events_with_events():
    EventHandler.reset_events()  # Reset events dictionary
    test_month = 3
    event1 = Event(test_month)
    event2 = Event(test_month)
    EventHandler.add_event(event1)
    EventHandler.add_event(event2)
    
    result = EventHandler.get_events(test_month)
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == event1
    assert result[1] == event2

def test_add_event():
    EventHandler.reset_events()  # Reset events dictionary
    test_month = 5
    test_event = Event(test_month)
    
    EventHandler.add_event(test_event)
    
    assert len(EventHandler.get_events(test_month)) == 1
    assert EventHandler.get_events(test_month)[0] == test_event
    
    EventHandler.add_event(test_event)
    
    assert len(EventHandler.get_events(test_month)) == 2
    assert EventHandler.get_events(test_month)[0] == test_event
    assert EventHandler.get_events(test_month)[1] == test_event

def test_add_multiple_events_to_same_month():
    EventHandler.reset_events()  # Reset events dictionary
    test_month = 10
    event1 = Event(test_month)
    event2 = Event(test_month)
    
    EventHandler.add_event(event1)
    EventHandler.add_event(event2)
    
    assert len(EventHandler.get_events(test_month)) == 2
    assert EventHandler.get_events(test_month)[0] == event1
    assert EventHandler.get_events(test_month)[1] == event2

def test_add_event_maintains_order():
    EventHandler.reset_events()  # Reset events dictionary
    test_month = 15
    event1 = Event(test_month)
    event2 = Event(test_month)
    event3 = Event(test_month)
    
    EventHandler.add_event(event1)
    EventHandler.add_event(event2)
    EventHandler.add_event(event3)
    
    assert len(EventHandler.get_events(test_month)) == 3
    assert EventHandler.get_events(test_month)[0] == event1
    assert EventHandler.get_events(test_month)[1] == event2
    assert EventHandler.get_events(test_month)[2] == event3