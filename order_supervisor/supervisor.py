import json
from datetime import datetime


class OrderSupervisor:

    WAKE_EVENTS = {
        "shipment_delayed",
        "customer_message_received",
        "refund_requested",
        "no_update_for_n_hours"
    }

    TERMINAL_EVENTS = {
        "delivered",
        "refund_resolved",
        "manual_termination"
    }

    def __init__(self):
        self.activity_log = []
        self.timeline = []
        self.memory_summary = []

        self.delay_count = 0
        self.escalated = False
        self.status = "ACTIVE"

        self.max_timeline_size = 5

    def message_customer(self, reason):
        self.activity_log.append(
            f"{datetime.now()} | MESSAGE_CUSTOMER | {reason}"
        )

    def message_logistics_team(self, reason):
        self.activity_log.append(
            f"{datetime.now()} | MESSAGE_LOGISTICS | {reason}"
        )

    def create_internal_note(self, note):
        self.activity_log.append(
            f"{datetime.now()} | INTERNAL_NOTE | {note}"
        )

    def escalate(self, reason):
        self.escalated = True

        self.activity_log.append(
            f"{datetime.now()} | ESCALATE | {reason}"
        )

    def mark_for_review(self, reason):
        self.activity_log.append(
            f"{datetime.now()} | REVIEW | {reason}"
        )

    def should_wake(self, event):

        if event in self.WAKE_EVENTS:
            return "WAKE_NOW"

        return "STAY_ASLEEP"


    def handle_event(self, event):

        if event == "shipment_delayed":

            self.delay_count += 1

            if self.delay_count == 1:

                self.message_customer(
                    "A shipment delay occurred and customer was informed."
                )

                self.message_logistics_team(
                    "Investigate shipment delay."
                )

                self.create_internal_note(
                    "First shipment delay detected."
                )

            else:

                self.escalate(
                    "Repeated shipment delays."
                )

                self.message_customer(
                    "Issue escalated due to repeated delays."
                )

        elif event == "customer_message_received":

            self.create_internal_note(
                "Customer contacted support."
            )

            if self.delay_count > 0:

                self.message_customer(
                    "Provided shipment update."
                )

        elif event == "refund_requested":

            self.create_internal_note(
                "Refund requested by customer."
            )

            self.escalate(
                "Refund review required."
            )

        elif event == "no_update_for_n_hours":

            self.message_logistics_team(
                "No shipment updates received."
            )

            self.mark_for_review(
                "Order stagnant."
            )

    def update_timeline(self, event):

        self.timeline.append(event)

        while len(self.timeline) > self.max_timeline_size:

            oldest = self.timeline.pop(0)

            self.memory_summary.append(
                f"{oldest.replace('_', ' ').title()} occurred."
            )

    def get_status(self):

        return {
            "status": self.status,
            "delay_count": self.delay_count,
            "escalated": self.escalated
        }


    def print_final_summary(self):

        print("\n" + "=" * 50)
        print("FINAL SUMMARY")
        print("=" * 50)

        print("\nStatus:")
        print(self.status)

        print("\nMemory Summary:")
        for item in self.memory_summary:
            print("-", item)

        print("\nRecent Timeline:")
        for item in self.timeline:
            print("-", item)

        print("\nActivity Log:")
        for item in self.activity_log:
            print("-", item)

        print("\nLearnings:")

        if self.delay_count > 0:
            print("- A shipment delay occurred and customer was informed..")

        if self.escalated:
            print("- Escalation was required.")

        if self.status == "COMPLETED":
            print("- Workflow reached a terminal state.")

    def run(self, events):

        print("Supervisor Started\n")

        event_counter = 0

        for event_record in events:

            event_counter += 1

            event = event_record["event"]

            print(f"Processing Event: {event}")

            wake_decision = self.should_wake(event)

            print(f"Wake Policy: {wake_decision}")

            self.update_timeline(event)

            if wake_decision == "WAKE_NOW":
                self.handle_event(event)

            if event_counter % 3 == 0:
                print("\nTimer Wake-Up Triggered")
                self.handle_event("no_update_for_n_hours")

            if event in self.TERMINAL_EVENTS:

                self.status = "COMPLETED"

                print(
                    f"\nTerminal Event Detected: {event}"
                )

                break

        self.print_final_summary()


def load_events(filename):

    with open(filename, "r") as f:
        return json.load(f)


if __name__ == "__main__":

    events = load_events("events.json")

    supervisor = OrderSupervisor()

    supervisor.run(events)