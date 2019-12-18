from flask import Flask, jsonify, request, render_template, redirect, url_for
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


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'GET':
        if request.args.get('hits') is None:
            return render_template('index.html', hits=None)
    if request.method == 'POST':
        keyword = request.form['keyword']
        recs_size = request.form['top_k']
        if not recs_size:
            recs_size = 5
        recs_size = int(recs_size)

        recs, res = inner_recommend(keyword, recs_size)

        return render_template('detail.html', hits=res['hits']['hits'], recs_size=len(recs), recs=recs)


def inner_recommend(keyword, rec_size=3):
        if not rec_size:
            rec_size = 5
        body = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["cn_name^10", "py_name", "en_name^10", "memo", "address", "tags", "city_cn", "city_en"]
                }
            }
        }
        res = es.search(index="poi", body=body, size=rec_size+1)
        recs = [{'pic': _r['_source']['pic'], 'cn_name': _r['_source']['cn_name']} for _r in res['hits']['hits']]
        return recs, res


@app.route('/just_recommend/<name>', methods=['GET'])
def just_recommend(name, rec_size=5):
    keyword = name
    if not rec_size:
        rec_size = 5
    recs_size = int(rec_size)

    recs, res = inner_recommend(keyword, recs_size)

    return render_template('recommend.html', current_item=res['hits']['hits'][0]['_source'], recs_size=len(recs), recs=recs)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
