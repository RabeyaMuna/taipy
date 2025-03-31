# #import os os.environ["TAIPY_GUI_WEBAPP_PATH"] = os.path.normpath( "/home/andre/taipyRepo/taipy/taipy/gui/webapp" )

from taipy.gui import Gui, notify, close_notification

def on_close(state, notification_id, reason):
    print(f"Notification {notification_id} closed due to {reason}")

# Function to trigger a notification
def send_notification(state):
    notify(state, "info", "This is a test notification!", None, None, "3", on_close)

# Function to close the notification
def close_test_notification(state):
    close_notification(state, "3", "forced")

if __name__ == "__main__":
    page = """
# Notification Demo

Click the button to trigger a notification:

<|button|text=Send Notification|on_action=send_notification|>

Click the button to close the notification:

<|button|text=Close Notification|on_action=close_test_notification|>
"""
Gui(page).run()
