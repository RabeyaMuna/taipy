from taipy.gui import Gui, notify, close_notification

# Function to trigger a notification
def send_notification(state):
    notify(state, "warning", "This is a test notification!", None, 3000, "3", "on_notification_closed")

# Function triggered when a notification is closed (from frontend) : NOT WORKING
def on_notification_closed(state, notification_id, reason=None):
    print("Notification closed from frontend")
    print(f"Notification {notification_id} closed from frontend. Reason: {reason}")

# Function triggered when a notification is closed manually
def on_close(state, notification_id, reason=None):
    print("Here")
    print(f"Notification {notification_id} closed, reason: {reason}")


# Function to close the notification manually
def close_test_notification(state):
    print("Manually closing notification 3...")
    close_notification(state, "3")

if __name__ == "__main__":
    page = """
# Notification Demo

Click the button to trigger a notification:

<|button|text=Send Notification|on_action=send_notification|>

Click the button to close the notification:

<|button|text=Close Notification|on_action=close_test_notification|>
"""

    Gui(page).run()