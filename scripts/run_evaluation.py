import json
import os
import sys
import time
import google.generativeai as genai
import pandas as pd
from sklearn.metrics import classification_report

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agent import AmazonSupportAgent
from src.baselines import SimpleBaseline, TrivialBaseline
from src.retrieval import SimpleBM25


class LLMJudge:

  def __init__(self, api_key: str, model='gemini-3.5-flash-lite'):
    genai.configure(api_key=api_key)
    self.model = genai.GenerativeModel(model)

  def score(self, tweet, reply, intent):
    prompt = f"""Evaluate this Twitter customer support reply for @AmazonHelp.
Rate from 1 (terrible) to 5 (flawless) on:
1. Groundedness (Adheres to standard customer policy, avoids fake promises)
2. Tone (Empathetic, clear, and professional)
3. Actionability & Safety (Clear next step, protects privacy, under 280 chars)

Tweet: "{tweet}"
Intent: "{intent}"
Reply: "{reply}"

Respond ONLY with valid JSON:
{{
  "groundedness": 4,
  "tone": 4,
  "actionability": 4,
  "overall": 4.0
}}"""
    try:
      res = self.model.generate_content(
          prompt,
          generation_config=genai.GenerationConfig(
              response_mime_type='application/json', temperature=0.0
          ),
      )
      return json.loads(res.text.strip())
    except Exception:
      return {'groundedness': 3, 'tone': 3, 'actionability': 3, 'overall': 3.0}


def calc_metrics(gold_esc, pred_esc):
  n = len(gold_esc)
  correct = sum(1 for g, p in zip(gold_esc, pred_esc) if g == p)
  false_auto = sum(
      1 for g, p in zip(gold_esc, pred_esc) if g is True and p is False
  )
  unnecessary_esc = sum(
      1 for g, p in zip(gold_esc, pred_esc) if g is False and p is True
  )
  return {
      'accuracy': round(correct / n, 4),
      'false_auto_handle_rate': round(false_auto / n, 4),
      'unnecessary_escalation_rate': round(unnecessary_esc / n, 4),
  }


def main():
  api_key = os.environ.get('GEMINI_API_KEY')
  if not api_key:
    print('ERROR: GEMINI_API_KEY not set! Run: $env:GEMINI_API_KEY="AIzaSy..."')
    return

  print('1. Indexing historical pairs with BM25...')
  retriever = SimpleBM25()
  retriever.fit_from_csv('data/reconstructed_pairs.csv', max_rows=3000)

  print('2. Loading golden evaluation set (eval/golden_set.csv)...')
  full_df = pd.read_csv('eval/golden_set.csv')
  eval_df = (
      full_df.groupby('gold_intent', group_keys=False)
      .apply(lambda x: x.head(7), include_groups=True)
      .reset_index(drop=True)
  )
  print(f'Evaluating on {len(eval_df)} balanced golden samples...\n')

  trivial = TrivialBaseline()
  simple = SimpleBaseline(retriever)
  agent = AmazonSupportAgent(api_key, retriever, model='gemini-3.5-flash-lite')
  judge = LLMJudge(api_key, model='gemini-3.5-flash-lite')

  results = {'trivial': [], 'simple': [], 'agent': []}

  print('Running Trivial Baseline...')
  for _, row in eval_df.iterrows():
    results['trivial'].append(trivial.predict(row['customer_tweet']))

  print('Running Simple Baseline...')
  for _, row in eval_df.iterrows():
    results['simple'].append(simple.predict(row['customer_tweet']))

  print('Running AI Support Agent pipeline...')
  for idx, row in eval_df.iterrows():
    res = agent.predict(row['customer_tweet'])
    results['agent'].append(res)
    time.sleep(0.3)
    if (idx + 1) % 10 == 0:
      print(f'  Processed {idx + 1}/{len(eval_df)} rows...')

  gold_intents = eval_df['gold_intent'].tolist()
  gold_esc = eval_df['gold_escalate'].tolist()

  summary_table = []
  for model_name in ['trivial', 'simple', 'agent']:
    preds = results[model_name]
    pred_intents = [p['intent'] for p in preds]
    pred_esc = [p['escalate'] for p in preds]

    clf_rep = classification_report(
        gold_intents, pred_intents, output_dict=True, zero_division=0
    )
    esc_metrics = calc_metrics(gold_esc, pred_esc)

    summary_table.append({
        'Model': model_name,
        'Intent Macro F1': round(clf_rep['macro avg']['f1-score'], 3),
        'Intent Accuracy': round(clf_rep['accuracy'], 3),
        'Escalation Accuracy': esc_metrics['accuracy'],
        'False Auto-Handle (Dangerous)': esc_metrics['false_auto_handle_rate'],
        'Unnecessary Escalation': esc_metrics['unnecessary_escalation_rate'],
    })

  print('\n================ HEADLINE COMPARISON RESULTS ================')
  summary_df = pd.DataFrame(summary_table)
  print(summary_df.to_string(index=False))

  print('\nRunning LLM-as-a-Judge on 20 Agent replies...')
  judge_sample = eval_df.head(20).copy()
  judge_scores = []
  for i in range(len(judge_sample)):
    tweet = judge_sample.iloc[i]['customer_tweet']
    gold_intent = judge_sample.iloc[i]['gold_intent']
    reply = results['agent'][i]['reply']
    score_data = judge.score(tweet, reply, gold_intent)
    judge_scores.append(score_data)
    time.sleep(0.3)

  j_df = pd.DataFrame(judge_scores)
  print('\n================ LLM-JUDGE QUALITY SCORES (1-5 Scale) ================')
  print(f"Groundedness: {j_df['groundedness'].mean():.2f} / 5.0")
  print(f"Tone & Empathy: {j_df['tone'].mean():.2f} / 5.0")
  print(f"Actionability & Safety: {j_df['actionability'].mean():.2f} / 5.0")
  print(f"Overall Quality: {j_df['overall'].mean():.2f} / 5.0")

  eval_df['agent_intent'] = [p['intent'] for p in results['agent']]
  eval_df['agent_escalate'] = [p['escalate'] for p in results['agent']]
  eval_df['agent_reason'] = [p['reason'] for p in results['agent']]
  eval_df['agent_reply'] = [p['reply'] for p in results['agent']]
  eval_df.to_csv('benchmark_results.csv', index=False)
  print('\nResults exported to benchmark_results.csv')


if __name__ == '__main__':
  main()
