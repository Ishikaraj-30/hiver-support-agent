import math
import re
from collections import Counter
import pandas as pd


def tokenize(text):
  return re.findall(r'\w+', str(text).lower())


class SimpleBM25:

  def __init__(self, k1=1.5, b=0.75):
    self.k1 = k1
    self.b = b
    self.corpus = []
    self.doc_len = []
    self.avgdl = 0.0
    self.df = Counter()
    self.idf = {}
    self.doc_freqs = []

  def fit_from_csv(self, csv_path, max_rows=3000):
    df = pd.read_csv(csv_path).dropna(subset=['customer_text', 'brand_text'])
    if len(df) > max_rows:
      df = df.sample(n=max_rows, random_state=42)

    for _, row in df.iterrows():
      cust = str(row['customer_text']).strip()
      brand = str(row['brand_text']).strip()
      if len(brand) < 15:
        continue
      self.corpus.append({'customer': cust, 'brand_reply': brand})
      tokens = tokenize(cust)
      self.doc_len.append(len(tokens))
      freq = Counter(tokens)
      self.doc_freqs.append(freq)
      for token in freq.keys():
        self.df[token] += 1

    n_docs = len(self.corpus)
    self.avgdl = sum(self.doc_len) / n_docs if n_docs > 0 else 0
    for token, freq in self.df.items():
      self.idf[token] = math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))

  def query(self, text, top_k=2):
    tokens = tokenize(text)
    scores = []
    for idx, freq in enumerate(self.doc_freqs):
      score = 0.0
      doc_len = self.doc_len[idx]
      for token in tokens:
        if token in freq:
          tf = freq[token]
          idf = self.idf.get(token, 0.0)
          num = tf * (self.k1 + 1)
          denom = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
          score += idf * (num / denom)
      scores.append((score, idx))

    scores.sort(key=lambda x: x[0], reverse=True)
    return [self.corpus[idx] for _, idx in scores[:top_k]]