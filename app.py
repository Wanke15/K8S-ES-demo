from datetime import datetime
from flask import Flask, jsonify, request, render_template
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts='localhost:9292')

app = Flask(__name__)


# @app.route('/', methods=['GET'])
# def index():
#     results = es.get(index='poi')
#     return jsonify(results['_source'])


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('index.html', hits=None)
    if request.method == 'POST':
        keyword = request.form['keyword']
        hits_size = request.form['top_k']
        if not hits_size:
            hits_size = 5
        # keyword = '张家界'
        # keyword = request.args.get('keyword')

        body = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["cn_name^10", "py_name", "en_name^10", "memo", "address", "tags", "city_cn", "city_en"]
                }
            }
        }

        res = es.search(index="poi", body=body, size=hits_size)

        # return jsonify(res['hits']['hits'])
        return render_template('index.html', hits=res['hits']['hits'], hits_size=int(hits_size))


@app.route('/insert_data', methods=['POST'])
def insert_data():
    slug = request.form['slug']
    title = request.form['title']
    content = request.form['content']

    body = {
        'slug': slug,
        'title': title,
        'content': content,
        'timestamp': datetime.now()
    }

    result = es.index(index='contents', id=slug, body=body)

    return jsonify(result)


# @app.route('/search', methods=['GET'])
def search():
    # keyword = request.form['keyword']
    # keyword = '张家界'
    keyword = request.args.get('keyword')

    body = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["cn_name^10", "py_name", "en_name^10", "memo", "address", "tags", "city_cn", "city_en"]
            }
        }
    }

    res = es.search(index="poi", body=body)

    return jsonify(res['hits']['hits'])


if __name__ == '__main__':
    app.run(port=5000, debug=True)
