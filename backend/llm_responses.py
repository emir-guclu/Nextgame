import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

DOT_ENV_PATH = "C:\\Projects\\game\\backend\\.env"

load_dotenv(DOT_ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY ortam değişkeni bulunamadı. Lütfen ayarlayın.")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # client = ai.Client(api_key=GEMINI_API_KEY, project="projects/854704284169")
    MODEL_NAME = "gemini-2.5-flash"
except:
    raise ValueError("API Bağlantısı sağlanamadı. Lütfen kontrol edin!")

SYSTEM_INSTRUCTION_EN = """
You are the 'NextGame Curator', a knowledgeable, helpful, and enthusiastic virtual assistant specializing in video games. You have extensive knowledge of game genres, themes, tags, and player preferences, especially regarding games on platforms like Steam.

Your primary task is to analyze a list of candidate games provided to you, based on a game the user likes. From this list, you must select EXACTLY THREE games:
1. Two games that are VERY SIMILAR to the user's liked game in terms of genre, theme, gameplay mechanics, or overall atmosphere. Label these as "Similar". Consider the provided genres and tags when making your selection.
2. One game that is an INTERESTING ALTERNATIVE. It should be a game that someone who likes the user's game might enjoy, but offers something different or unexpected – perhaps a related subgenre, a unique take on familiar mechanics, or an indie gem they might have missed. Label this as "Alternative".

You will be given the name of the user's liked game and a list containing the names, genres, and tags of the candidate games. Make your selections using ONLY the information from the provided candidate list. Do not invent games or details not present in the list.

Your response MUST be ONLY a valid JSON object strictly adhering to the following schema. Do NOT include any introductory text, concluding sentences, markdown formatting (like ```json), or any other text outside the JSON structure.

{
  "recommendations": [
    {
      "game_name": "The Exact Name of the Chosen Game from the Candidate List",
      "type": "Similar" | "Alternative", // Only one of these two values
      "match_reason": "A brief, concise explanation (1-2 sentences) of why this game is similar or a good alternative, referencing genres, tags, or themes.",
      "user_note": "A friendly and short note (1-2 sentences) directed at the user (e.g., 'You'll especially love the X in this game:' or 'If you enjoyed Y, you'll definitely like Z.')"
    },
    // Exactly two more objects following this structure (total of three recommendations)
  ]
}

Use a friendly, knowledgeable, and concise tone, as if talking to a fellow gamer, but be clear. Focus on providing clear justifications based on the provided game details. Ensure the game names you select exactly match the names given in the candidate list.
"""

CONFIG = {
    "temperature" : 0.2,
    "top_p" : 0.95,
    "top_k" : 64,
    "max_output_tokens" : 8192,
    "response_mime_type" : "application/json"
}

SAFETY_SETTINGS = [
  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    safety_settings=SAFETY_SETTINGS,
    generation_config=CONFIG, # type: ignore
    system_instruction=SYSTEM_INSTRUCTION_EN
)

def get_llm_analysis_for_embedding(candidate_games : list[str], language : str = "en") -> list[dict]:
    """
    SentenceTransformer modelinin belirlediği embeddingten gelen verilerle
    kullanıcıya 3 adet öneride bulunmasına sağlayan fonksiyon
    """

    if not candidate_games:
        return []
    

    # Dil'e göre değişecek kısımlar
    if language == "tr":
        reason_instruction = "Explain briefly (1-2 sentences) in Turkish why it's similar or a good alternative, referencing specific details FROM THE PROVIDED TEXT for that game."
        note_instruction = "Write a short, friendly, and engaging note for the user in Turkish about the chosen game, based on the details in its provided text (e.g., 'Bu oyunda özellikle şunu sevebilirsin:' or 'Eğer X'i sevdiysen, Y'ye bayılacaksın.')."
        output_language_instruction = "Ensure the 'match_reason' and 'user_note' fields are in Turkish."
    else: # Varsayılan İngilizce
        reason_instruction = "Explain briefly (1-2 sentences) in English why it's similar or a good alternative, referencing specific details FROM THE PROVIDED TEXT for that game."
        note_instruction = "Write a short, friendly, and engaging note for the user in English about the chosen game, based on the details in its provided text (e.g., 'You'll especially love the X in this game:' or 'If you enjoyed Y, you'll definitely like Z.')"
        output_language_instruction = "Ensure the 'match_reason' and 'user_note' fields are in English."


    prompt = f"""
    Analyze the detailed descriptions of the 20 candidate games provided below. Based *solely* on these descriptions, select exactly 3 games that stand out as particularly interesting or high-quality recommendations.

    Consider factors like uniqueness, genre representation, potential appeal based on common gaming interests suggested by the descriptions, etc. Try to select a diverse set if possible.

    Candidate Games (Full Details - Analyze each text carefully):
    {candidate_games}
    {output_language_instruction}
    Required Output Format (VALID JSON ONLY - no extra text before or after):
    {{
    "recommendations": [
        {{
        "game_name": "The Exact Name of the Chosen Game (Extract accurately from the text provided for the candidate)",
        "type": "Interesting", // 'type' alanını şimdilik genel tutalım
        "match_reason": "{reason_instruction}",
        "user_note": "{note_instruction}"
        }},
        // Exactly two more recommendation objects following this structure
    ]
    }}
    """

    response = None
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[len("```json"):].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-len("```")].strip()
        
        result_json = json.loads(response_text)
        
        recomendations = result_json.get("recommendations", [])

        return recomendations
    except json.JSONDecodeError as json_err:
        # JSON ayrıştırma sırasında hata olursa burası çalışır
        print(f"❗️ HATA: LLM yanıtı geçerli bir JSON formatında değil veya bozuk.")
        print(f"   Detay: {json_err}")
        print(f"   Alınan Ham Yanıt:\n---\n{response.text}\n---")
        # Güvenli bir şekilde boş liste döndür
        return []

    except Exception as e:
        # API isteği veya başka beklenmedik bir hata olursa burası çalışır
        print(f"❗️ LLM isteği sırasında genel bir hata oluştu: {e}")
        # Hata nedenini daha detaylı görmek için prompt_feedback'i kontrol et (varsa)
        try:
            if response is None:
                print("   Prompt Feedback")
                return []
            print("   Prompt Feedback:", response.prompt_feedback)
        except AttributeError:
            pass # Eğer response objesi oluşmadıysa veya feedback yoksa
        try:
            if response is None:
                print("   Any Error, Not Feedback")
                return []

            # v1beta için güvenlik ve bitiş nedeni kontrolü
            if hasattr(response, 'candidates') and response.candidates:
                print("   Finish Reason:", response.candidates[0].finish_reason)
                print("   Safety Ratings:", response.candidates[0].safety_ratings)
        except AttributeError:
             pass
        # Güvenli bir şekilde boş liste döndür
        return []