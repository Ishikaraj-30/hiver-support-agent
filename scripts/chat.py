import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import AmazonSupportAgent
from src.retrieval import SimpleBM25


def main():
  api_key = os.environ.get("GEMINI_API_KEY")
  if not api_key:
    print("Please set GEMINI_API_KEY first!")
    return

  print("Loading historical support pairs for grounding...")
  retriever = SimpleBM25()
  retriever.fit_from_csv("data/reconstructed_pairs.csv", max_rows=1000)

  agent = AmazonSupportAgent(api_key, retriever, model="gemini-3.5-flash-lite")

  print(
      "\n=== @AmazonHelp Support Agent (Type 'exit' or 'quit' to stop) ===\n"
  )

  while True:
    try:
      tweet = input("Customer Tweet > ").strip()
      if not tweet or tweet.lower() in ["quit", "exit"]:
        print("Exiting chat session.")
        break

      res = agent.predict(tweet)

      print(f"\nAgent Reply    > {res['reply']}")
      print(f"Classification > Intent: {res['intent']} | Escalate: {res['escalate']}")
      print(f"Policy Reason  > {res['reason']}\n" + "-" * 50 + "\n")

    except (KeyboardInterrupt, EOFError):
      print("\nExiting chat session.")
      break


if __name__ == "__main__":
  main()
  