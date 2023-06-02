from flask import Flask, request, jsonify,render_template
import spacy
from flask_cors import CORS
import openai


app = Flask(__name__)
CORS(app) 

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')



@app.route('/process-text', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data.get('text')  

    
    processed_text = tag_verbs_or_adverbs(text)

    
    response = {'result': processed_text}
    return jsonify(response)


@app.route('/translate', methods=['POST'])
def process_text_2():
    data = request.get_json()
    text = data.get('text')  

    
    processed_text = openai_transmation(text)  

    
    response = {'result': processed_text}
    return jsonify(response)






def tag_verbs_or_adverbs(text):
    nlp =spacy.load("en_core_web_sm", disable=["ner"])
    doc = nlp(text)

    tagged_text = ""
    for token in doc:
        #print(f"{token.text:<15} {token.dep_:<10} {token.head.text:<15}")
        if (token.dep_ == "ROOT" or token.dep_ == "auxpass"or token.dep_ == "relcl"or token.dep_ == "xcomp"or token.dep_ == "acl"or token.dep_ == "aux"or token.dep_ == "cop")and (token.text!="to")or((token.dep_ =="pcomp"or token.dep_ =="pobj"or token.dep_ =="conj"or token.dep_ == "ccomp")and (token.pos_=="VERB"or token.pos_=="AUX")or(token.text!="in" and token.dep_ == "advcl")):
            tagged_text += f'<font color="red">{token.text}</font> '
        else:
            tagged_text += f"{token.text} "

    return tagged_text.strip()


def openai_transmation(text):
    openai.api_key = "sk-9bSXmFB4kZN5wKKKbW3ibG5ptJTdqcFzvDbfatQavLOj4IUO"
    openai.api_base = 'https://api.chatanywhere.cn/v1'
    trans_response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Translate the following English text to Chinese: \n {text}"}])

    return trans_response['choices'][0]['message']['content']




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5214)

