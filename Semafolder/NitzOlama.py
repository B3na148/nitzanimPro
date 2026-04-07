import json
import re
import ollama


class LocalAnalyzer:
    def __init__(self, model_name="llama3.2:3b"):
        """
        Initializes the analyzer with a specific LLM and sets up category counters.
        """
        self.model = model_name
        # Defined categories for counting and classification
        self.counts = {
            "Education": 0,
            "Entertainment": 0,
            "Games": 0,
            "Adult": 0,
            "Other": 0
        }
        print(f"✓ Analyzer started (model: {self.model})")

    def classify_titles(self, titles):
        """
        Sends a batch of titles to the LLM and extracts JSON responses using Regex.
        """
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

            # Regex to find all JSON objects regardless of AI conversational filler
            json_matches = re.findall(r'\{.*?\}', raw_content, re.DOTALL)

            results = []
            for match in json_matches:
                try:
                    obj = json.loads(match)
                    results.append(obj)
                except json.JSONDecodeError:
                    continue

            return results
        except Exception as e:
            print(f"Classification error: {e}")
            return []

    def apply_force_filter(self, data):
        """
        Manually verifies categories and increments the counters.
        This acts as a 'hard-coded' safety net for the AI's output.
        """
        allowed = list(self.counts.keys())

        for item in data:
            title = item.get("title", "").lower()

            # Rule-based correction (prioritizes certain keywords)
            if any(word in title for word in ["history", "python", "equation", "recipe", "lesson", "calculus"]):
                item["category"] = "Education"
            elif any(word in title for word in ["game", "minecraft", "play", "strategy", "clash"]):
                item["category"] = "Games"

            # Fallback for unrecognized categories
            if item.get("category") not in allowed:
                item["category"] = "Other"

            # Increment the counter for the final category
            self.counts[item["category"]] += 1

        return data

    def run_analysis(self, input_file, output_file):
        """
        Main execution loop: reads input, processes in batches, and saves the report.
        """
        try:
            # Reset counters before starting a new run
            self.counts = {k: 0 for k in self.counts}

            with open(input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)

            # Extract titles from the 'history' key in the input JSON
            titles = [entry.get("title") for entry in input_data.get("history", []) if entry.get("title")]
            print(f"-> Total titles to process: {len(titles)}")

            batch_size = 20
            final_results = []

            for i in range(0, len(titles), batch_size):
                print(f"-> Processing batch {i // batch_size + 1}...")
                batch = titles[i:i + batch_size]

                # Step 1: LLM Classification
                raw_results = self.classify_titles(batch)

                # Step 2: Filtering and Counting
                processed_results = self.apply_force_filter(raw_results)

                final_results.extend(processed_results)

            # Prepare the final report structure
            report_data = {
                "summary": {
                    "total_urls": len(final_results),
                    "category_counts": self.counts
                },
                "details": final_results
            }

            # Save the complete report with statistics to the output file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=4)

            print(f"✓ Success! Data saved to {output_file}")

            # Print a summary to the console for quick reference
            print("\n" + "=" * 30)
            print("RUN SUMMARY:")
            for cat, val in self.counts.items():
                print(f"{cat}: {val}")
            print("=" * 30)

        except FileNotFoundError:
            print(f"Error: The file '{input_file}' was not found.")
        except Exception as e:
            print(f"Critical error: {e}")


if __name__ == "__main__":
    # Ensure 'history_data.json' exists in the same directory before running
    analyzer = LocalAnalyzer()
    analyzer.run_analysis("history_data.json", "final_report.json")
