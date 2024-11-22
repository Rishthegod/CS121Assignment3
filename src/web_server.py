from flask import Flask, request
from index_search import search

app = Flask(__name__, static_url_path='/', static_folder='static')

@app.route("/search")
def perform_search():
    query = request.args.get('q')
    if not query: return { 'error': 'Query must be present' }

    return search(query)


if __name__ == '__main__':
    app.run('0.0.0.0', 6100)

