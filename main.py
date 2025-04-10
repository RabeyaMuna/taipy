from taipy.gui import Gui, notify, close_notification

# Function triggered when a notification is closed
def on_close(state, notification_id, reason):
    print(f"Notification {notification_id} closed ")

# Function to trigger a notification
def send_notification(state):
    notify(state, "warning", "This is a test notification!", None, 3000, "3", on_close)

# Function to close the notification manually
def close_test_notification(state):
    print("Manually closing notification 3...")
    close_notification(state, "3", "forced")
    
def on_delete_notification(state, snackbarId, reason):
    print(f"Notification {snackbarId} deleted, reason: {reason}")

if __name__ == "__main__":
    page = """
# Notification Demo

Click the button to trigger a notification:

<|button|text=Send Notification|on_action=send_notification|>

Click the button to close the notification:

<|button|text=Close Notification|on_action=close_test_notification|>
"""
    Gui(page).run()
    Gui.on_action("DeleteNotification", on_delete_notification)