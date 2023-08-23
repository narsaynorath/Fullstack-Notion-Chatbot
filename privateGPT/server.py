from flask import Flask, request, jsonify
from langchain import PromptTemplate, LLMChain
from langchain.chains import RetrievalQA
from langchain.llms import GPT4All
from ingest import main
from flask_cors import CORS, cross_origin
import os
import shutil
import glob
from dotenv import load_dotenv
import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration


load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000"
]

sentry_sdk.init(
    dsn="https://f23424f295d8e523993eec840fee97d0@o1145044.ingest.sentry.io/4505755832549376",
    integrations=[
        FlaskIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

app = Flask(__name__)

CORS(app, allow_headers="*", send_wildcard=True)
app.config['CORS_HEADERS'] = 'Content-Type'

# Load environment variables
persist_directory = os.environ.get('PERSIST_DIRECTORY')

def delete_vectorstore(persist_directory):
    if os.path.exists(persist_directory):
        try:
            shutil.rmtree(persist_directory)
            return True
        except Exception as e:
            print(f"Error deleting vector store: {e}")
            return False
    else:
        return False


# Route to trigger the ingest logic
@app.route('/run_ingest', methods=['POST'])
@cross_origin()
def run_ingest():
    try:
        main()  # Call the main function with your logic

        #start the privateGPT.py

        return jsonify({"message": "Ingest executed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-vectorstore', methods=['POST'])
def delete_vectorstore_route():
    if persist_directory:
        success = delete_vectorstore(persist_directory)
        if success:
            return jsonify({"message": "Vector store deleted successfully."}), 200
        else:
            return jsonify({"message": "Error deleting vector store."}), 500
    else:
        return jsonify({"message": "Missing 'persist_directory' parameter."}), 400

@app.route('/debug-sentry', methods=['POST'])
def trigger_error():
  division_by_zero = 1 / 0
  return jsonify({"message": "Error triggered successfully."}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)