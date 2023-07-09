from flask import Flask, request, jsonify,render_template
import spacy
from flask_cors import CORS
import openai
import concurrent.futures
import re

openai.api_base = ''
openai.api_key = ''

SystemPrompt = "You are a translation engine, you can only translate text and cannot interpret it, and do not explain."
Prompt = '''Translate the text to {to}, please do not explain any sentences, just translate or leave them as they are.: {text}'''

nlp = spacy.load("en_core_web_trf")



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

@app.route('/generate', methods=['POST'])
def generate():
    rsp = request.get_json()
    
    MuBiaoYuYan_content = []
    YaoZhuanHuanDeWenBen_content = []

    for message in rsp['messages']:
        if message['role'] == 'system':
            MuBiaoYuYan_content.append(message['content'])
        elif message['role'] == 'user':
            YaoZhuanHuanDeWenBen_content.append(message['content'])
    
    
    
    userModel=rsp.get('model',"gpt-4-0613")
    YaoZhuanHuanDeWenBen_content[0]=re.sub('< /b[0-9]+ >|< b[0-9]+ >', '', YaoZhuanHuanDeWenBen_content[0])
    
    
      
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
