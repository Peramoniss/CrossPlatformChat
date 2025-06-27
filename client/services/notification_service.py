from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget
from client.views.notification_widget import NotificationWidget

class NotificationManager:
    """
    A class to manage a pop-up error message.
    """

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.queue = []
        self.active_notification = None

    def show_notification(self, message, duration=4000):
        """
        Shows a pop-up error message. If already showing a notification, queues the message.

        :param message: The error message.
        :param duration: Duration that the message will stay in screen, in milisseconds. Default
        """

        self.queue.append((message, duration))
        if not self.active_notification:
            self._show_next()

    def _show_next(self):
        """
        Shows the next message, if any, on the queue.
        """
        
        if not self.queue:
            return

        message, duration = self.queue.pop(0)
        self.active_notification = NotificationWidget(message, duration, parent=self.parent)
        notif = self.active_notification
        notif.setFixedWidth(300)

        def place_and_show():
            notif.adjustSize()
            margin = 15
            x = self.parent.width() - notif.width() - margin
            y = self.parent.height() - notif.height() - margin
            notif.move(x, y)
            notif.show()

        QTimer.singleShot(0, place_and_show)
        notif.closed.connect(self._on_notification_finished)

    def _on_notification_finished(self):
        """
        When the time is over, turns the notification off.
        """
        self.active_notification = None
        self._show_next()
