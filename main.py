from taipy.gui import Gui, notify

# Function to trigger a notification
def send_notification(state):
    notify(state, "warning", "This is a test notification!", None, None, "3", "on_notification_closed")

# Function triggered when a notification is closed (from frontend)
def on_notification_closed(state, notification_id, reason=None):
    print("Notification closed from frontend")
    print(f"Notification {notification_id} closed from frontend. Reason: {reason}")

# GUI page setup
page = """
# Notification Demo

Click the button to trigger a notification:

<|button|text=Send Notification|on_action=send_notification|>
"""

if __name__ == "__main__":
    Gui(page).run()