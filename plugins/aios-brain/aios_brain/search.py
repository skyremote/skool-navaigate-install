"""FTS5 BM25 relevance multiplied by a bounded, 30-day recency boost."""
import math
import re
import time
from . import db


def search(conn, query, limit=8, recency=True, half_life_days=30):
    terms = re.findall(r'\w+',query,flags=re.U)[:24]
    if not terms:
        raise ValueError('Enter at least one search word')
    if half_life_days <= 0:
        raise ValueError('half_life_days must be positive')
    match = ' AND '.join('"'+word+'"' for word in terms)
    rows = conn.execute('''SELECT d.*,i.title,bm25(search_index) AS rank,
        snippet(search_index,0,'[',']',' ... ',36) AS snippet
        FROM search_index JOIN documents d ON d.rowid=search_index.rowid
        JOIN items i ON i.ref=d.ref WHERE search_index MATCH ?
        ORDER BY rank LIMIT 500''',(match,)).fetchall()
    now = time.time()
    hits = []
    for row in rows:
        factor = 1 + math.pow(2,-max(0,now-row['ts'])/(half_life_days*86400)) if recency else 1
        hits.append({'ref':row['ref'],'kind':row['kind'],'title':row['title'],
                     'timestamp':row['ts'],'score':-row['rank']*factor,'snippet':row['snippet']})
    return sorted(hits,key=lambda h:h['score'],reverse=True)[:max(1,min(int(limit),50))]


def read(conn, ref, start=0, max_chars=12000):
    value = db.bundle(conn,ref)
    body = '\n\n'.join(d['role']+': '+d['body'] for d in value['documents'])
    start = max(0,int(start))
    size = max(1,min(int(max_chars),60000))
    return {'ref':ref,'title':value['item']['title'],'text':body[start:start+size],
            'total_chars':len(body),'next_start':start+size if start+size<len(body) else None}
