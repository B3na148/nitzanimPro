import json
import re
import ollama


class LocalAnalyzer:
    def __init__(self, model_name="llama3.2:latest"):
        self.model = model_name
        self.counts = {
            "Education": 0,
            "Entertainment": 0,
            "Games": 0,
            "Adult": 0,
            "Other": 0
        }
        print(f"✓ Analyzer started (model: {self.model})")

    def classify_titles(self, items):
        prompt = f"""
                You are a high-precision data classifier. 
                Task: Classify the following list of search titles into EXACTLY ONE of these categories: 
                "Education", "Entertainment", "Games", "Adult", or "Other".

                Rules:
                1. Return ONLY a valid JSON list of objects.
                2. Do not include any introductory text, explanations, or markdown code blocks.
                3. If a title is ambiguous, classify it as "Other".
                4. Use the exact keys: "title" and "category".

                Example Output:
                [
                    {{"title": "How to learn Python", "category": "Education"}},
                    {{"title": "Minecraft Free Play", "category": "Games"}}
                ]

                Items to classify:
                {json.dumps(items, ensure_ascii=False)}
                """
        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
            raw_content = response['message']['content']
            json_matches = re.findall(r'\{.*?\}', raw_content, re.DOTALL)

            results = []
            for match in json_matches:
                try:
                    clean_match = match.replace("'", '"')
                    obj = json.loads(clean_match)
                    results.append(obj)
                except json.JSONDecodeError:
                    continue
            return results
        except Exception as e:
            print(f"Classification error: {e}")
            return []

    def apply_force_filter(self, data):
        allowed = list(self.counts.keys())
        processed = []
        for item in data:
            if not isinstance(item, dict): continue
            cat = item.get("category", "Other")
            if cat not in allowed:
                cat = "Other"
            item["category"] = cat
            self.counts[cat] += 1
            processed.append(item)
        return processed

    def generate_personality_verdict(self):

        stats_str = ", ".join([f"{k}: {v}" for k, v in self.counts.items() if v > 0])


        prompt = f"""
        Based on this search history statistics: {stats_str}.
        Write a very short, witty summary (5 sentences).
        """

        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content'].strip()
        except Exception as e:
            return "a model problem."

    def run_analysis(self, input_file, output_file):
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)

            if isinstance(input_data, list):
                items = [str(x) for x in input_data if x]
            elif isinstance(input_data, dict):
                items = [entry.get("title") for entry in input_data.get("history", []) if entry.get("title")]
            else:
                raise ValueError("Unsupported JSON format")

            print(f"-> Total items to process: {len(items)}")

            batch_size = 8
            final_results = []

            for i in range(0, len(items), batch_size):
                print(f"-> Processing batch {i // batch_size + 1}...")
                batch = items[i:i + batch_size]
                raw_results = self.classify_titles(batch)
                processed_results = self.apply_force_filter(raw_results)
                final_results.extend(processed_results)


            print("-> Generating final verdict...")
            verdict = self.generate_personality_verdict()

            report_data = {
                "summary": {
                    "total_processed": len(final_results),
                    "category_counts": self.counts,
                    "ai_verdict": verdict
                },
                "details": final_results
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=4)

            print(f"✓ Success! Data saved to {output_file}")
            print("\n" + "=" * 20)
            print("RUN SUMMARY:")
            for cat, val in self.counts.items():
                print(f"{cat}: {val}")
            print("-" * 20)
            print(f"AI VERDICT: {verdict}")
            print("=" * 20)

        except FileNotFoundError:
            print(f"Error: '{input_file}' not found.")
        except Exception as e:
            print(f"Critical error: {e}")


if __name__ == "__main__":
    analyzer = LocalAnalyzer()

    analyzer.run_analysis("history_data.json", "final_report.json")
