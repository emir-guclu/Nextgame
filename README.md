# 🎮 NextGame Recommendation Engine

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is a web application that provides personalized game recommendations using semantic similarity and AI curation based on a game entered by the user.

## ✨ Features

* **Intelligent Search:** Autocompletes game names as you type, suggesting existing games from the database.
* **Semantic Recommendations:** Finds games most similar to your input using vector similarity (Sentence Transformers) calculated from game descriptions and metadata.
* **AI Curation:** Sends the list of similar games to the Google Gemini 2.5 Flash model to select the top 3 most interesting ones and generate unique comments (why it's recommended, who it's for) for each.
* **Multi-Language Support:** Offers Turkish and English language options for UI texts and LLM-generated recommendation comments.
* **Modern Interface:** A simple, clean web interface with a dark mode theme.

## 🛠️ Technologies Used

* **Backend:**
    * Python 3.9+
    * FastAPI (Asynchronous web framework)
    * Uvicorn (ASGI server)
    * SQLAlchemy (ORM for database interaction)
    * SQLite (Development database)
    * Sentence Transformers (`all-MiniLM-L6-v2`) (For text embeddings)
    * Scikit-learn (For calculating cosine similarity)
    * Google Generative AI SDK (`google-genai`) (For Gemini API interaction)
    * Pandas & PyArrow (For data processing and reading Parquet)
    * NumPy (For vector operations)
    * python-dotenv (For API key management)
* **Frontend:**
    * HTML5
    * CSS3
    * Vanilla JavaScript (For API requests and DOM manipulation)
* **Data:**
    * Processed and combined Steam game datasets (sourced from Kaggle).
    * Game metadata and embedding vectors are stored in an SQLite database.

## 🏗️ Architecture Flow (Simple)

1.  **User Input:** Search for a game name starts from the frontend.
2.  **Search API (`/search/`):** FastAPI receives the request and calls the function in `crud.py`.
3.  **Database (Search):** `crud.py` fetches matching game names and header images from the SQLite database.
4.  **Frontend (Search Results):** Results are returned to the frontend, displaying the autocomplete list.
5.  **User Selection:** User selects a game and clicks the "Get Recommendations" button.
6.  **Recommendation API (`/recommend/`):** FastAPI receives the request (with game name and language).
7.  **Database (Similarity):** `crud.py` fetches the target game's vector and all other vectors, calculates cosine similarity, and returns the `text_for_embedding` data for the top 20 similar games.
8.  **LLM Service (`llm_responses.py`):** The backend sends these 20 texts and the selected language to the Google Gemini 2.5 Flash model.
9.  **AI Analysis:** Gemini analyzes the texts, selects 3 games, and generates comments (reason, note) in JSON format.
10. **Frontend (Recommendations):** The results are returned to the frontend, displaying the recommendation cards.

## 📸 Screenshots

\[Add a few screenshots or a short GIF of the running application here. E.g., search box, recommendation results.]

## 🚀 Setup and Run

Follow these steps to run the project locally:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git](https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git)
    cd YOUR_PROJECT_NAME
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Key:**
    * Create a file named `.env` in the root directory of the project.
    * Add your API key obtained from Google AI Studio into it:
        ```env
        GEMINI_API_KEY=YOUR_API_KEY_HERE
        ```

5.  **Prepare the Database:**
    * **IMPORTANT:** This repository does not include the large data files (`.parquet`, `.db`) due to size limits.
    * You need to obtain the necessary `data_with_embeddings.parquet` file (or generate it using the data processing scripts \[mention script names if applicable]). Place this file in the project's root directory.
    * Run the following command to create the database (`nextgame.db`) and populate it with data (This might take a few moments):
        ```bash
        python populate_db.py
        ```
        *(Note: Ensure the `populate_db.py` script points to the correct Parquet file path.)*

6.  **Start the Server:**
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    *(Or add `--port YOUR_PORT_NUMBER` if you want to use a different port.)*

7.  **Open the Application:**
    Navigate to `http://127.0.0.1:8000` (or your specified port) in your web browser.

## 📝 API Endpoints (Brief)

* `GET /`: Serves the frontend `index.html` file.
* `GET /search/?q={query}`: Returns game names and header images starting with the given `query` (for autocomplete).
* `GET /recommend/?game_name={name}&lang={en|tr}`: Returns 3 game recommendations for the specified `game_name` in the requested `lang` (default 'en').

## 🌱 Future Improvements (Ideas)

* User accounts and Steam integration (`User` model).
* Personalized recommendations based on the user's owned games.
* More efficient vector search using PostgreSQL with the `pgvector` extension.
* Advanced filtering options (genre, tags, price range, etc.).
* Addition of Collaborative Filtering methods.
* Rewriting the frontend with a modern framework like Next.js or React.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---