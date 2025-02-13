"""
Event handling module.

This module provides a simple event handling system. It allows registering
handlers for specific events and dispatching events to the registered
handlers.
"""


class EventHandler:
    """
    Event handling class.

    This class provides a simple event handling system. It allows registering
    handlers for specific events and dispatching events to the registered
    handlers.
    """

    def __init__(self):
        """
        Initialize the event handler.

        This method initializes the event handler by setting the handlers
        dictionary to an empty dictionary.
        """
        self.handlers = {}

    def register(self, event, handler):
        """
        Register a handler for an event.

        This method takes an event and a handler function as arguments. It
        adds the handler to the list of handlers for the given event.

        :param event: The event to register the handler for.
        :param handler: The handler function to register.
        """
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

    def unregister(self, event, handler):
        """
        Unregister a handler for an event.

        This method takes an event and a handler function as arguments. It
        removes the handler from the list of handlers for the given event.

        :param event: The event to unregister the handler for.
        :param handler: The handler function to unregister.
        """
        if event in self.handlers:
            self.handlers[event].remove(handler)

    def dispatch(self, event, *args, **kwargs):
        """
        Dispatch an event to the registered handlers.

        This method takes an event and optional arguments as arguments. It
        calls all the handlers registered for the given event with the given
        arguments.

        :param event: The event to dispatch.
        :param args: Optional positional arguments to pass to the handlers.
        :param kwargs: Optional keyword arguments to pass to the handlers.
        """
        if event in self.handlers:
            for handler in self.handlers[event]:
                handler(*args, **kwargs)
