import os
from twilio.rest import Client


class Notify:
    def __init__(self, sid: str, auth: str, admin_number: str, client_number: str) -> None:
        self.account_sid = sid
        self.auth_token = auth
        self.client = Client(self.account_sid, self.auth_token)
        self.message = None
        self.call = None
        self.admin_number = admin_number
        self.client_number = client_number

    def notify_me(self, msg: str) -> str:
        self.message = self.client.messages \
            .create(
            body=f"{msg}",
            from_=self.admin_number,
            to=self.client_number,
        )
        print(f"Message sent from {self.admin_number} to {self.client_number}, the message said {msg}.")
        return self.message.sid

    def make_a_call(self):
        self.call = self.client.calls.create(
            url='http://demo.twilio.com/docs/voice.xml',
            to=self.client_number,
            from_=self.admin_number
        )
