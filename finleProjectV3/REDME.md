
Hello and welcome to Benaya and Sioma's final project!

The goal of this project is to raise awareness for parents about their child's internet usage.

**Here is how we did it:**
* We built a Chrome extension that pulls the user's Google search history.
* We send that data to a server (hosted locally on our own computer for the demo), which is handled by `server.py`.
* We analyze this data using `categorization.py` and save the results in a file called `final_report.json`. 
  > **NOTE:** The categorization part requires a local Ollama model. We used the Qwen model for the presentation because it is lightweight.
* Finally, we take `final_report.json` and visually represent the data using `interface.py`.

### Setting Up the Extension
To get the extension running, follow these steps:

1. Click on the **Extensions icon** (the puzzle piece) at the top right of your browser.
2. Click on **Manage extensions**.
3. Toggle on **Developer mode** (usually located in the top right corner).
4. Click the **Load unpacked** button.
5. Select the `extension` directory from this project's folder.
6. You should be all set up!
