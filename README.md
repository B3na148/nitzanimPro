
# Welcome to Benaya and Semyon's Final Project!

The goal of this project is to promote digital safety by providing parents with clear insights into their child’s internet usage.

### How it Works:
Our system operates through a seamless pipeline of data collection, AI analysis, and visualization:

* **Data Collection:** We developed a **Chrome Extension** that retrieves the user's browsing history using the Chrome History API.
* **Data Transmission:** This data is sent to a local backend server managed by `server.py`.
* **AI Categorization:** The script `categorization.py` processes the raw URLs and titles. It uses a local **Ollama** instance running the **Llama 3.2** model to classify activities into specific categories (e.g., Education, Games, Adult).
    > **Note:** We chose **Llama 3.2** because it offers an excellent balance between speed and accuracy for text classification.
* **Storage:** The analyzed data is structured and saved into `final_report.json`.
* **Visualization:** Finally, `interface.py` reads the report and generates a graphical dashboard to represent the findings visually.

> [!IMPORTANT]
> **Performance Note:** Depending on your hardware specifications and the size of the history being processed, the AI analysis may take several minutes to complete.

---

### Extension Installation Guide
To set up the browser extension for the demo, follow these steps:

1.  Open Chrome and click the **Extensions icon** (puzzle piece) in the top-right corner.
2.  Select **Manage Extensions** from the menu.
3.  In the top-right corner of the Extensions page, toggle **Developer mode** to **ON**.
4.  Click the **Load unpacked** button that appears in the top-left.
5.  Navigate to your project folder and select the `extension` directory.
6.  The extension is now active and ready to sync with your local server!

---

### System Requirements
To run this project successfully, ensure you have the following installed:
* **Python 3.2**
* **Ollama** (with the `llama3.2` model downloaded: `ollama run llama3.2`)
* NOTE: you can select lighter model like Qwen model. and change it in model name.
* **Google Chrome Browser**

*note to start the program just run the interface.py file.
*finle note, i putted a example for finle report in the server folder so you don't have to run the model :)
