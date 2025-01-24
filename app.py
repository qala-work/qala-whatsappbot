from dotenv import load_dotenv
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio import rest
import requests
from utils import *
import re

app = Flask(__name__)

load_dotenv()
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = rest.Client(account_sid, auth_token)
twilio_base = "https://api.twilio.com"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = os.environ.get("SECRET_KEY")
prelim_columns = [
    {
        "column": "fullname",
        "question": "Please give me your full name.",
    },
    {
        "column": "socialmedia",
        "question": "What are some of your social media links we can look at to gain a better understanding of you? This is completely optional.",
    },
    {
        "column": "fulltime",
        "question": "This is a full time role based in {}. This is non-negotiable. Are you able to commit to a full time role?\n\nReply only with YES or NO".format(
            os.environ["LOCATION"]
        ),
    },
    {
        "column": "start",
        "question": "Are you ready to begin the assessment?",
    },
]


def send_response(message, media=None):

    resp = MessagingResponse()
    msg = resp.message(message)

    if media:
        msg = resp.message(message)
        msg.media(media)
    return str(resp)


@app.route("/whatsapp", methods=["POST"])
def respond_to_whatsapp():

    candidate_response = request.values.get("Body", "")
    candidate_number = request.values.get("WaId", "")

    candidate_email = check_phonenumber(candidate_number)

    if candidate_email:

        if check_completed(candidate_email):

            consent = check_feedback_consent(candidate_email)

            if consent is None:

                set_feedback_consent(candidate_email, candidate_response)

                consent = check_feedback_consent(candidate_email)

                if consent:

                    feedback_questions = get_feedback_questions()

                    return send_response(feedback_questions[0])

            if consent is False:

                return send_response(
                    "Thank you for successfully completing the screening assessment for the Court Order {} role, {}. We will be in touch soon. Contact careers@courtorder.co.za for any queries.".format(
                        os.environ["JOB_ROLE"], os.environ["LOCATION"]
                    )
                )

            else:

                feedback_questions = get_feedback_questions()

                print(feedback_questions)
                for i in range(len(feedback_questions)):

                    if not check_feedback_answer(candidate_email, i):

                        print("index", i)

                        if not update_feedback(candidate_email, candidate_response):
                            return send_response(
                                "An error occurred while saving your response. Please resend your answer.\n"
                                + feedback_questions[i]
                            )

                        if i < len(feedback_questions) - 1:

                            return send_response(feedback_questions[i + 1])

            return send_response(
                "You have successfully completed the screening assessment for the Court Order {} role, {}. We will be in touch soon. Contact careers@courtorder.co.za for any queries.".format(
                    os.environ["JOB_ROLE"], os.environ["LOCATION"]
                )
            )

        for i in range(len(prelim_columns)):
            column = prelim_columns[i]["column"]

            if not check_column(column, candidate_email):

                if not update_other(candidate_email, candidate_response, column):
                    return send_response(
                        "An error occurred while saving your response. Please resend your answer.\n"
                        + prelim_columns[i]["question"]
                    )

                if i < len(prelim_columns) - 1:

                    if prelim_columns[i + 1]["column"] == "start":
                        return send_response(
                            prelim_columns[i + 1]["question"],
                            media=os.environ["INTRO_VIDEO"],
                        )

                    return send_response(prelim_columns[i + 1]["question"])

                questions = get_questions()
                return send_response(questions[0])

        questions = get_questions()
        print(questions)
        for i in range(len(questions)):

            if not check_answer(candidate_email, i):

                print("index", i)

                try:
                    print(request.values.get("NumMedia", ""))
                    print(request.values.get("MediaContentType0", ""))
                    if (
                        request.values.get("NumMedia", "") != "1"
                        or request.values.get("MediaContentType0", "") != "video/mp4"
                    ):
                        return send_response(
                            "Please upload a valid video to answer the question. Contact careers@courtorder.co.za for any queries."
                        )

                    candidate_response = request.values.get("MediaUrl0", "")

                except:
                    return send_response(
                        "Please upload a valid video to answer the question. Contact careers@courtorder.co.za for any queries."
                    )

                if not update_answer(candidate_email, candidate_response):
                    return send_response(
                        "An error occurred while saving your response. Please resend your answer.\n"
                        + questions[i]
                    )

                if i < len(questions) - 1:

                    print(questions[i + 1])

                    return send_response(questions[i + 1])

        set_completed(candidate_email)

        return send_response(
            "Congratulations! You have completed the screening assessment. We're keen to always improve our interviewing process. Could you provide us with honest feedback (text only) about your interview experience? Please answer with a YES or NO."
        )

    else:

        try:
            email = re.search(r"[\w\.-]+@[\w\.-]+", candidate_response).group()

            if new_candidate(candidate_number, email):
                return send_response(prelim_columns[0]["question"])
            else:
                return send_response(
                    "An error occurred while saving your response. What is the email id with which you applied for this role?"
                )

        except:
            return send_response(
                "Welcome to the screening assessment for the {} role at Court Order for {} store. What is the email id with which you applied for this role?".format(
                    os.environ["JOB_ROLE"], os.environ["LOCATION"]
                )
            )


if __name__ == "__main__":
    app.run(debug=True)
