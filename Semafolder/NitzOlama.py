import json
import re
import ollama


class LocalAnalyzer:
    def __init__(self, model_name="llama3.2:3b"):
        self.model = model_name
        print(f"✓ Analyzer started (model: {self.model})")

    def classify_titles(self, titles):
        """Classifies titles using LLM, using regex to extract JSON from any text format"""

        prompt = f"""
        You are a browser history classifier. Assign each title to ONE of these categories:
        "Education", "Entertainment", "Games", "Adult", "Other".

        Return ONLY valid JSON objects, each on a new line, following this format:
        {{"title": "title", "category": "category"}}

        Titles: {json.dumps(titles, ensure_ascii=False)}
        """

        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
            raw_content = response['message']['content']

            # The "Bulletproof" Regex: find all substrings that look like JSON objects
            # This completely ignores Markdown backticks, headers, or conversational filler
            json_matches = re.findall(r'\{.*?\}', raw_content, re.DOTALL)

            results = []
            for match in json_matches:
                try:
                    obj = json.loads(match)
                    results.append(obj)
                except json.JSONDecodeError:
                    continue

            print(f"DEBUG: Found {len(results)} valid JSON objects.")
            return results
        except Exception as e:
            print(f"Classification error: {e}")
            return []

    def apply_force_filter(self, data):
        """Ensures that only permitted categories are used via hard-coded rules"""
        allowed = ["Education", "Entertainment", "Games", "Adult", "Other"]
        for item in data:
            title = item.get("title", "").lower()

            # Smart keyword-based correction
            if any(word in title for word in ["history", "python", "equation", "recipe", "lesson", "calculus"]):
                item["category"] = "Education"
            elif any(word in title for word in ["game", "minecraft", "play", "strategy"]):
                item["category"] = "Games"

            # If the AI assigned a category not in our list, force it to 'Other'
            if item.get("category") not in allowed:
                item["category"] = "Other"
        return data

    def run_analysis(self, input_file, output_file):
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            titles = [entry.get("title") for entry in data.get("history", []) if entry.get("title")]
            print(f"-> Total titles to process: {len(titles)}")

            # Processing in batches of 20 for memory stability
            batch_size = 20
            final_results = []
            for i in range(0, len(titles), batch_size):
                print(f"-> Processing batch {i // batch_size + 1}...")
                batch = titles[i:i + batch_size]
                results = self.classify_titles(batch)
                final_results.extend(self.apply_force_filter(results))

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(final_results, f, ensure_ascii=False, indent=4)

            print(f"✓ Success! Report saved in {output_file}")

        except Exception as e:
            print(f"Critical error: {e}")


if __name__ == "__main__":
    analyzer = LocalAnalyzer()
    analyzer.run_analysis("history_data.json", "final_report.json")