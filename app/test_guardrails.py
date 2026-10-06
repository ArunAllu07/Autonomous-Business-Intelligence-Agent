from app.guardrails import (
    requires_approval,
    request_approval
)


def main():

    action = "DELETE"

    if requires_approval(action):

        approved = request_approval(action)

        if approved:
            print("\nACTION APPROVED")
        else:
            print("\nACTION REJECTED")

    else:

        print("\nNO APPROVAL REQUIRED")


if __name__ == "__main__":
    main()