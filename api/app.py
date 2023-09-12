# -*- coding:utf-8 -*-
import asyncio
import datetime
import http.client
import json
import logging
import os
import traceback
import uuid

import dotenv
import openai
import requests
from celery import Celery
from celery.result import AsyncResult
from flask import Flask, request, send_from_directory, jsonify, Response
from langchain import VectorDBQA, OpenAI
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
# from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from qdrant_client.models import PointIdsList

from core.settings import settings
from error import bad_request
from worker import ingest_worker

from extensions import ext_storage, ext_qdrant, ext_celery
from extensions.ext_storage import storage
from extensions.ext_qdrant import qdrantins

logger = logging.getLogger(__name__)

def create_app() -> Flask:
    app = Flask(__name__)

    app.config.from_object(settings)
    app.config["UPLOAD_FOLDER"] = "storage"

    initialize_extensions(app)

    return app

def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    ext_storage.init_app(app, app.config["UPLOAD_FOLDER"])
    ext_qdrant.init_app(app)
    ext_celery.init_app(app)


# loading the .env file
dotenv.load_dotenv()

# load the prompts
with open("prompts/combine_prompt.txt", "r") as f:
    template = f.read()

with open("prompts/combine_prompt_hist.txt", "r") as f:
    template_hist = f.read()

with open("prompts/question_prompt.txt", "r") as f:
    template_quest = f.read()

with open("prompts/chat_combine_prompt.txt", "r") as f:
    chat_combine_template = f.read()

with open("prompts/chat_reduce_prompt.txt", "r") as f:
    chat_reduce_template = f.read()

embeddings_key_set = settings.EMBEDDINGS_KEY is not None
gpt_model = 'gpt-3.5-turbo'

app = create_app()
celery = app.extensions["celery"]

mongo = MongoClient(app.config["MONGO_URI"])
db = mongo["docassis"]
vectors_collection = db["vectors"]


async def async_generate(chain, question, chat_history):
    result = await chain.arun({"question": question, "chat_history": chat_history})
    return result


def run_async_chain(chain, question, chat_history):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = {}
    try:
        answer = loop.run_until_complete(async_generate(chain, question, chat_history))
    finally:
        loop.close()
    result["answer"] = answer
    return result


def get_vectorstore(data):
    return ""


def get_docsearch(vectorstore, embeddings_key):
    return qdrantins.qdrantvectorstore


@celery.task(bind=True)
def ingest(self, directory, formats, name_job, filename, user):
    resp = ingest_worker(self, directory, formats, name_job, filename, user)
    return resp


def complete_stream(question, docsearch, chat_history, api_key):
    openai.api_key = api_key
    if is_azure_configured():
        logger.debug("in Azure")
        openai.api_type = "azure"
        openai.api_version = settings.AZURE_OPENAI_API_VERSION
        openai.api_base = settings.AZURE_OPENAI_API_BASE
        llm = AzureChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=settings.AZURE_OPENAI_API_BASE,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            deployment_name=settings.AZURE_DEPLOYMENT_NAME,
        )
    else:
        logger.debug("plain OpenAI")
        llm = ChatOpenAI(openai_api_key=api_key)
    docs = docsearch.similarity_search(question, k=4)
    # join all page_content together with a newline
    print(docs)
    docs_together = "\n".join([doc.page_content for doc in docs])
    p_chat_combine = chat_combine_template.replace("{summaries}", docs_together)
    messages_combine = [{"role": "system", "content": p_chat_combine}]
    for doc in docs:
        if doc.metadata:
            data = json.dumps({"type": "source", "doc": doc.page_content, "metadata": doc.metadata})
        else:
            data = json.dumps({"type": "source", "doc": doc.page_content})
        yield f"data:{data}\n\n"

    if len(chat_history) > 1:
        tokens_current_history = 0
        # count tokens in history
        chat_history.reverse()
        for i in chat_history:
            if "prompt" in i and "response" in i:
                tokens_batch = llm.get_num_tokens(i["prompt"]) + llm.get_num_tokens(i["response"])
                if tokens_current_history + tokens_batch < settings.TOKENS_MAX_HISTORY:
                    tokens_current_history += tokens_batch
                    messages_combine.append({"role": "user", "content": i["prompt"]})
                    messages_combine.append({"role": "system", "content": i["response"]})
    messages_combine.append({"role": "user", "content": question})
    completion = openai.ChatCompletion.create(model=gpt_model, engine=settings.AZURE_DEPLOYMENT_NAME,
                                              messages=messages_combine, stream=True, max_tokens=2000, temperature=0)

    for line in completion:
        if "content" in line["choices"][0]["delta"]:
            # check if the delta contains content
            data = json.dumps({"answer": str(line["choices"][0]["delta"]["content"])})
            yield f"data: {data}\n\n"
    # send data.type = "end" to indicate that the stream has ended as json
    data = json.dumps({"type": "end"})
    yield f"data: {data}\n\n"


@app.route("/stream", methods=["POST"])
def stream():
    data = request.get_json()
    # get parameter from url question
    question = data["question"]
    history = data["history"]
    # history to json object from string
    history = json.loads(history)

    if not embeddings_key_set:
        embeddings_key = data["embeddings_key"]
    else:
        embeddings_key = settings.EMBEDDINGS_KEY
    if "active_docs" in data:
        vectorstore = get_vectorstore({"active_docs": data["active_docs"]})
    else:
        vectorstore = ""
    docsearch = get_docsearch(vectorstore, embeddings_key)

    # question = "Hi"
    return Response(
        complete_stream(question, docsearch, chat_history=history, api_key=settings.API_KEY), mimetype="text/event-stream"
    )


def is_azure_configured():
    return settings.AZURE_OPENAI_API_BASE and settings.AZURE_OPENAI_API_VERSION and settings.AZURE_DEPLOYMENT_NAME


@app.route("/api/answer", methods=["POST"])
def api_answer():
    data = request.get_json()
    question = data["question"]
    history = data["history"]
    print("-" * 5)
    if not embeddings_key_set:
        embeddings_key = data["embeddings_key"]
    else:
        embeddings_key = settings.EMBEDDINGS_KEY

    # use try and except  to check for exception
    try:
        # check if the vectorstore is set
        vectorstore = get_vectorstore(data)
        # loading the index and the store and the prompt template
        # Note if you have used other embeddings than OpenAI, you need to change the embeddings
        docsearch = get_docsearch(vectorstore, embeddings_key)

        q_prompt = PromptTemplate(
            input_variables=["context", "question"], template=template_quest, template_format="jinja2"
        )
        if settings.LLM_NAME == "openai_chat":
            if is_azure_configured():
                logger.debug("in Azure")
                llm = AzureChatOpenAI(
                    openai_api_key=settings.API_KEY,
                    openai_api_base=settings.AZURE_OPENAI_API_BASE,
                    openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                    deployment_name=settings.AZURE_DEPLOYMENT_NAME,
                )
            else:
                logger.debug("plain OpenAI")
                llm = ChatOpenAI(openai_api_key=settings.API_KEY, model_name=gpt_model)  # optional parameter: model_name="gpt-4"
            messages_combine = [SystemMessagePromptTemplate.from_template(chat_combine_template)]
            if history:
                tokens_current_history = 0
                # count tokens in history
                history.reverse()
                for i in history:
                    if "prompt" in i and "response" in i:
                        tokens_batch = llm.get_num_tokens(i["prompt"]) + llm.get_num_tokens(i["response"])
                        if tokens_current_history + tokens_batch < settings.TOKENS_MAX_HISTORY:
                            tokens_current_history += tokens_batch
                            messages_combine.append(HumanMessagePromptTemplate.from_template(i["prompt"]))
                            messages_combine.append(AIMessagePromptTemplate.from_template(i["response"]))
            messages_combine.append(HumanMessagePromptTemplate.from_template("{question}"))
            p_chat_combine = ChatPromptTemplate.from_messages(messages_combine)
        elif settings.LLM_NAME == "openai":
            llm = OpenAI(openai_api_key=settings.API_KEY, temperature=0)
        else:
            raise ValueError("unknown LLM model")

        if settings.LLM_NAME == "openai_chat":
            question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
            doc_chain = load_qa_chain(llm, chain_type="map_reduce", combine_prompt=p_chat_combine)
            chain = ConversationalRetrievalChain(
                retriever=docsearch.as_retriever(k=4),
                question_generator=question_generator,
                combine_docs_chain=doc_chain,
            )
            chat_history = []
            # result = chain({"question": question, "chat_history": chat_history})
            # generate async with async generate method
            result = run_async_chain(chain, question, chat_history)

        else:
            qa_chain = load_qa_chain(
                llm=llm, chain_type="map_reduce", combine_prompt=chat_combine_template, question_prompt=q_prompt
            )
            chain = VectorDBQA(combine_documents_chain=qa_chain, vectorstore=docsearch, k=3)
            result = chain({"query": question})

        print(result)

        # some formatting for the frontend
        if "result" in result:
            result["answer"] = result["result"]
        result["answer"] = result["answer"].replace("\\n", "\n")
        try:
            result["answer"] = result["answer"].split("SOURCES:")[0]
        except Exception:
            pass

        sources = docsearch.similarity_search(question, k=4)
        sources_doc = []
        for doc in sources:
            if doc.metadata:
                sources_doc.append({'title': doc.metadata['title'], 'text': doc.page_content})
            else:
                sources_doc.append({'title': doc.page_content, 'text': doc.page_content})
        result['sources'] = sources_doc

        # mock result
        # result = {
        #     "answer": "The answer is 42",
        #     "sources": ["https://en.wikipedia.org/wiki/42_(number)", "https://en.wikipedia.org/wiki/42_(number)"]
        # }
        return result
    except Exception as e:
        # print whole traceback
        traceback.print_exc()
        print(str(e))
        return bad_request(500, str(e))


@app.route("/api/docs_check", methods=["POST"])
def check_docs():
    return {"status": "exists"}


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json()
    question = data["question"]
    answer = data["answer"]
    feedback = data["feedback"]

    print("-" * 5)
    print("Question: " + question)
    print("Answer: " + answer)
    print("Feedback: " + feedback)
    print("-" * 5)
    response = requests.post(
        url="",
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps({"answer": answer, "question": question, "feedback": feedback}),
    )
    return {"status": http.client.responses.get(response.status_code, "ok")}


@app.route("/api/combine", methods=["GET"])
def combined_json():
    user = "local"
    """Provide json file with combined available indexes."""

    data = [
        {
            "name": "default",
            "filename": "default",
            "language": "default",
            "version": "",
            "description": "default",
            "date": "default",
            "pointids": [],
            "model": settings.EMBEDDINGS_NAME,
            "location": "local",
        }
    ]
    # structure: name, language, version, description, date, docLink
    # append data from vectors_collection
    for index in vectors_collection.find({"user": user}):
        location = index["location"].replace('\\', '/')
        data.append(
            {
                "name": index["name"],
                "filename": index["filename"],
                "language": index["language"],
                "version": "",
                "description": index["name"],
                "date": index["date"],
                "pointids": index["pointids"],
                "model": settings.EMBEDDINGS_NAME,
                "location": location,
            }
        )

    return jsonify(data)


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Upload a file to get vectorized and indexed."""
    if "user" not in request.form:
        return {"status": "no user"}
    user = secure_filename(request.form["user"])
    if "name" not in request.form:
        return {"status": "no name"}
    job_name = request.form["name"]
    # check if the post request has the file part
    if "file" not in request.files:
        print("No file part")
        return {"status": "no file"}
    file = request.files["file"]
    if file.filename == "":
        return {"status": "no file name"}

    if file:
        file_uuid = str(uuid.uuid4())
        extension = file.filename.split('.')[-1]
        filename = file_uuid + '.' + extension
        storage.save(filename, file.read())

        task = ingest.delay("temp", [".pdf", ".docx", ".csv", ".epub", ".md", "rst", "html", "mdx"], job_name, filename, user)
        # task id
        task_id = task.id
        return {"status": "ok", "task_id": task_id}
    else:
        return {"status": "error"}


@app.route("/api/task_status", methods=["GET"])
def task_status():
    """Get celery job status."""
    task_id = request.args.get("task_id")
    task = AsyncResult(task_id)
    task_meta = task.info
    return {"status": task.status, "result": task_meta}


### Backgound task api
@app.route("/api/upload_index", methods=["POST"])
def upload_index_files():
    if "user" not in request.form:
        return {"status": "no user"}
    user = secure_filename(request.form["user"])
    if "name" not in request.form:
        return {"status": "no name"}
    job_name = request.form["name"]
    if "filename" not in request.form:
        return {"status": "no filename"}
    filename = request.form["filename"]
    if "pointids" not in request.form:
        print("No pointids")
        return {"status": "no pointids"}
    pointidsstr = request.form["pointids"]
    pointids = pointidsstr.split(",")
    save_dir = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    # create entry in vectors_collection
    vectors_collection.insert_one(
        {
            "user": user,
            "name": job_name,
            "language": job_name,
            "location": save_dir,
            "pointids": pointids,
            "filename": filename,
            "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "model": settings.EMBEDDINGS_NAME,
            "type": "local",
        }
    )
    return {"status": "ok"}


@app.route("/api/download", methods=["get"])
def download_file():
    # user = secure_filename(request.args.get("user"))
    # job_name = secure_filename(request.args.get("name"))
    filename = secure_filename(request.args.get("file"))
    save_dir = os.path.join(app.config["UPLOAD_FOLDER"])
    return send_from_directory(save_dir, filename, as_attachment=True)


@app.route("/api/delete_old", methods=["get"])
def delete_old():
    """Delete old indexes."""
    path = request.args.get("path")
    dirs = path.split("/")
    dirs_clean = []
    for i in range(1, len(dirs)):
        dirs_clean.append(secure_filename(dirs[i]))
    path_clean = "/".join(dirs)
    winpath = path.replace("/", "\\")
    try:
        collection_one = vectors_collection.find_one({"location": path}) or vectors_collection.find_one({"location": winpath})
        if collection_one:
            qdrantins.client.delete(collection_name=settings.QDRANT_COLLECTION_NAME, points_selector=PointIdsList(points=collection_one["pointids"]))
        vectors_collection.delete_one({"location": path})
        vectors_collection.delete_one({"location": winpath})
        os.remove(path_clean)
    except FileNotFoundError:
        # return {"status": "error"}
        pass
    return {"status": "ok"}


# handling CORS
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


if __name__ == "__main__":
    app.run(debug=True, port=7091)
