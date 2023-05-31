from flask import Flask, request, jsonify
import spacy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有的跨域请求


@app.route('/process-text', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data.get('text')  # 获取选中的文本

    # 在这里进行文本处理和分析
    processed_text = tag_verbs_or_adverbs(text)

    # 将处理后的结果返回给 JavaScript 端
    response = {'result': processed_text}
    return jsonify(response)

def tag_verbs_or_adverbs(text):
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(text)

    tagged_text = ""
    for token in doc:
        #print(f"{token.text:<15} {token.dep_:<10} {token.head.text:<15}")
        if (token.dep_ == "ROOT" or token.dep_ == "auxpass"or token.dep_ == "relcl"or token.dep_ == "xcomp"or token.dep_ == "acl"or token.dep_ == "aux"or token.dep_ == "cop")and (token.text!="to")or((token.dep_ =="pcomp"or token.dep_ =="pobj"or token.dep_ =="conj"or token.dep_ == "ccomp")and (token.pos_=="VERB"or token.pos_=="AUX")or(token.text!="in" and token.dep_ == "advcl")):
            tagged_text += f'<font color="red">{token.text}</font> '
        else:
            tagged_text += f"{token.text} "

    return tagged_text.strip()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

