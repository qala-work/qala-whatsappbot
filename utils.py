from supabase import create_client, Client
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import docx
import PyPDF2
import os
from dotenv import load_dotenv

import assemblyai as aai

load_dotenv()

CANDIDATE_TABLE = "candidate_DURBAN"
QUESTIONS_TABLE = "bot_questions"
FEEDBACK_TABLE = "feedback_questions"


from dotenv import load_dotenv
import os

load_dotenv()

aai.settings.api_key = os.environ["ASSEMBLY_API_KEY"]


def assemblyai_transcribe(url):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(url)

    if transcript.status == aai.TranscriptStatus.error:
        print(transcript.error)

        return False
    else:
        print(transcript.text)

        return transcript.text


def update_transcripts(email):

    supabase = get_supabase()

    response = (
        supabase.table(CANDIDATE_TABLE).select("answers").eq("email", email).execute()
    )

    try:

        if len(response.data[0]["answers"]) > 0:

            transcripts = []

            for url in response.data[0]["answers"]:

                transcripts.append(assemblyai_transcribe(url))

            supabase.table(CANDIDATE_TABLE).update({"transcription": transcripts}).eq(
                "email", email
            ).execute()

            return True

    except Exception as e:
        print("ASSEMBLYAI ERROR:", e)
        return False


def get_supabase():

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_ROLE")
    supabase: Client = create_client(url, key)

    return supabase


def new_candidate(phonenumber, email):

    supabase = get_supabase()

    try:

        supabase.table(CANDIDATE_TABLE).insert(
            {
                "phone_number": phonenumber,
                "email": email,
                "location": os.environ.get("LOCATION"),
            }
        ).execute()
        return True
    except Exception as e:
        print(e)
        return False


def get_questions():

    supabase = get_supabase()

    response = supabase.table(QUESTIONS_TABLE).select("*").execute()

    try:

        questions = []
        for question in response.data:

            questions.append(question["question"])

        return questions

    except Exception as e:

        print(e)
        return False


def check_started(email: str):

    supabase = get_supabase()

    response = supabase.table(CANDIDATE_TABLE).select("*").eq("email", email).execute()

    try:

        if len(response.data) > 0:
            if response.data[0]["started"] == True:

                return True

    except Exception as e:

        print(e)
        return False


def check_completed(email: str):

    supabase = get_supabase()

    response = supabase.table(CANDIDATE_TABLE).select("*").eq("email", email).execute()

    try:

        if len(response.data) > 0:
            if response.data[0]["completed"] == True:

                return True

    except Exception as e:

        print(e)
        return False


def check_phonenumber(phonenumber):

    supabase = get_supabase()

    response = (
        supabase.table(CANDIDATE_TABLE)
        .select("*")
        .eq("phone_number", phonenumber)
        .execute()
    )

    try:

        if len(response.data) > 0:
            return response.data[0]["email"]
    except Exception as e:

        print(e)
        return False


def check_column(column, email):

    supabase = get_supabase()

    response = supabase.table(CANDIDATE_TABLE).select("*").eq("email", email).execute()

    try:

        if len(response.data) > 0:
            if response.data[0][column] is not None:

                return True
    except Exception as e:

        print(e)
        return False


def set_completed(email):
    supabase = get_supabase()

    response = supabase.table(CANDIDATE_TABLE).select("*").eq("email", email).execute()

    try:

        if len(response.data) > 0:

            # update_transcripts(email)

            response = (
                supabase.table(CANDIDATE_TABLE)
                .update({"completed": True})
                .eq("email", email)
                .execute()
            )

            return True

    except Exception as e:
        print(e)
        return False


def update_other(email, data, column):

    supabase = get_supabase()

    response = supabase.table(CANDIDATE_TABLE).select("*").eq("email", email).execute()

    try:

        if len(response.data) > 0:

            if column == "fulltime":
                data = True if data.lower() == "yes" else False

            if column == "start":
                data = True

            response = (
                supabase.table(CANDIDATE_TABLE)
                .update({column: data})
                .eq("email", email)
                .execute()
            )

            return True

    except Exception as e:
        print(e)
        return False


def update_answer(email, data):

    supabase = get_supabase()

    response = (
        supabase.table(CANDIDATE_TABLE).select("answers").eq("email", email).execute()
    )

    try:

        if response.data[0]["answers"] is None:

            response = (
                supabase.table(CANDIDATE_TABLE)
                .update({"answers": [data]})
                .eq("email", email)
                .execute()
            )

            return True

        else:

            print("existing answers: ", response.data[0]["answers"])

            answers = response.data[0]["answers"]
            answers.append(data)

            response = (
                supabase.table(CANDIDATE_TABLE)
                .update({"answers": answers})
                .eq("email", email)
                .execute()
            )

            return True

    except Exception as e:

        print(e)
        return False


def check_answer(email, index):

    supabase = get_supabase()

    response = (
        supabase.table(CANDIDATE_TABLE).select("answers").eq("email", email).execute()
    )

    try:

        if response.data[0]["answers"] is None:

            return False

        if len(response.data[0]["answers"]) > 0:

            if len(response.data[0]["answers"]) - 1 < index:

                return False

            return True
    except Exception as e:

        print(e)
        return False


def get_feedback_questions():

    supabase = get_supabase()

    response = supabase.table(FEEDBACK_TABLE).select("*").execute()

    try:

        questions = []
        for question in response.data:

            questions.append(question["question"])

        return questions

    except Exception as e:

        print(e)
        return False


def set_feedback_consent(email, data):

    supabase = get_supabase()

    response = supabase.table(CANDIDATE_TABLE).select("*").eq("email", email).execute()

    try:

        if len(response.data) > 0:

            data = True if data.lower() == "yes" else False

            response = (
                supabase.table(CANDIDATE_TABLE)
                .update({"feedback_consent": data})
                .eq("email", email)
                .execute()
            )

            return True

    except Exception as e:
        print(e)
        return False


def check_feedback_consent(email: str):

    supabase = get_supabase()

    response = supabase.table(CANDIDATE_TABLE).select("*").eq("email", email).execute()

    try:

        if len(response.data) > 0:

            return response.data[0]["feedback_consent"]

    except Exception as e:

        print(e)
        return False


def check_feedback_answer(email, index):

    supabase = get_supabase()

    response = (
        supabase.table(CANDIDATE_TABLE)
        .select("feedback_answers")
        .eq("email", email)
        .execute()
    )

    try:

        if response.data[0]["feedback_answers"] is None:

            return False

        if len(response.data[0]["feedback_answers"]) > 0:

            if len(response.data[0]["feedback_answers"]) - 1 < index:

                return False

            return True
    except Exception as e:

        print(e)
        return False


def update_feedback(email, data):

    supabase = get_supabase()

    response = (
        supabase.table(CANDIDATE_TABLE)
        .select("feedback_answers")
        .eq("email", email)
        .execute()
    )

    try:

        if response.data[0]["feedback_answers"] is None:

            response = (
                supabase.table(CANDIDATE_TABLE)
                .update({"feedback_answers": [data]})
                .eq("email", email)
                .execute()
            )

            return True

        else:

            print("existing answers: ", response.data[0]["feedback_answers"])

            answers = response.data[0]["feedback_answers"]
            answers.append(data)

            response = (
                supabase.table(CANDIDATE_TABLE)
                .update({"feedback_answers": answers})
                .eq("email", email)
                .execute()
            )

            return True

    except Exception as e:

        print(e)
        return False
