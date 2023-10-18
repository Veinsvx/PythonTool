import spacy
from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import openai
import concurrent.futures
import re
import requests

SystemPrompt = "You are a great translation engine, you can only translate text and cannot interpret it, and do not explain."
Prompt = '''Translate the text to {to}, please do not explain any sentences, just translate or leave them as they are.: {text}'''


nlp = spacy.load("en_core_web_trf")
app = Flask(__name__)
CORS(app) 

#app = Flask(__name__)
#CORS(app) 

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    rsp = request.get_json()
    
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        api_key = auth_header[7:]
        openai.api_key=api_key
    else:
        openai.api_key = 'sk-UZgUvlLyygKM4x9r7a295e9fA2F64847B328798803DbE4Fd'
    
    
    YaoZhuanHuanDeWenBen_content = []

    for message in rsp['messages']:
        if message['role'] == 'system':
            if message['content']!="":
                openai.api_base=message['content']
            else:
                openai.api_base="https://fast.xeduapi.com/v1"
        elif message['role'] == 'user':
            YaoZhuanHuanDeWenBen_content.append(message['content'])
    
    userModel=rsp.get('model',"gpt-3.5-turbo")
    YaoZhuanHuanDeWenBen_content[0]=re.sub('< *(/)?b *[0-9]+ *>', '', YaoZhuanHuanDeWenBen_content[0])
    
    if userModel == "gpt-4":
        openai.api_base="https://api.naga.ac/v1"
        openai.api_key="XeHMx3t60gTx3tgTcRX6m_mkWfoHQa6_ZA3H6xIE_cI"
    
    #print(openai.api_base)
    #print(openai.api_key)
    #print(userModel)
      
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(tag_verbs_or_adverbs, YaoZhuanHuanDeWenBen_content[0])
        future2 = executor.submit(openai.ChatCompletion.create, model=userModel, messages=[
            {"role": "system", "content": SystemPrompt},
            {"role": "user", "content": Prompt.format(to="chinese", text=YaoZhuanHuanDeWenBen_content[0])}
        ])

        modified_prompt = future1.result()
        response = future2.result()

    response['choices'][0]['message']['content'] = modified_prompt + ' \n ' + '<span class="transparent-text" style="opacity: 0.1;">'+response['choices'][0]['message']['content'].strip()+'</span>'
    return jsonify(response)


#def tag_verbs_or_adverbs(text):
#    response = requests.post("http://192.3.165.101:8246/tag_text", json={"text": text})
#    if response.status_code == 200:
#        tagged_text = response.json()["tagged_text"]
#        return tagged_text.strip()
#    else:
#        return text


def tag_verbs_or_adverbs(text):
    doc = nlp(text)

    tagged_text = ""
    for token in doc:
        if (token.dep_ == "ROOT" or token.dep_ == "auxpass"or token.dep_ == "relcl"or token.dep_ == "xcomp"or token.dep_ == "acl"or token.dep_ == "aux"or token.dep_ == "cop")and (token.text!="to")or((token.dep_ =="pcomp"or token.dep_ =="pobj"or token.dep_ =="conj"or token.dep_ == "ccomp")and (token.pos_=="VERB"or token.pos_=="AUX")or(token.text!="in" and token.dep_ == "advcl")):
            tagged_text += f'<span style="color: red;">{token.text}</span> '
        else:
            tagged_text += f"{token.text} "

    return tagged_text.strip()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5214)
