import streamlit as st
import tempfile
from supabase_client import init_supabase, supabase, BUCKET_NAME
from whisper_utils import transcribe_audio
import openai

openai.api_key = st.secrets["openai_api_key"]

supabase_url = st.secrets["supabase_url"]
supabase_key = st.secrets["supabase_key"]
init_supabase(supabase_url, supabase_key)

st.set_page_config(page_title="Coach Pitch & DISC - GENUP2050", layout="centered")
st.title("Coach Pitch & DISC - GENUP2050")

video_file = st.file_uploader("Téléverse ta vidéo de pitch", type=["mp4", "mov", "m4a", "wav", "mp3"])

if video_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=video_file.name) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    st.success("Vidéo reçue. Transcription en cours...")

    try:
        transcription = transcribe_audio(temp_file_path)
        st.text_area("Transcription :", transcription, height=200)

        profile = st.selectbox(
            "Quel est ton profil DISC ?",
            ["Dominant (D)", "Influent (I)", "Stable (S)", "Conforme (C)"]
        )

        def generate_feedback(text, disc_type):
            # Correction de la syntaxe de la chaîne formatée
            prompt = f"""
            Tu es un coach virtuel DISC.
            Le profil de la personne est : {disc_type}.
            Voici son pitch transcrit :
            {text}

            Donne un retour constructif, empathique, adapté au style {disc_type} avec des conseils concrets.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            return response["choices"][0]["message"]["content"]

        if profile and transcription:
            feedback = generate_feedback(transcription, profile)
            st.markdown("### Feedback IA personnalisé selon ton profil DISC :")
            st.info(feedback)

        try:
            # Suppression de l'ancienne vidéo sur Supabase
            supabase.storage.from_(BUCKET_NAME).remove([video_file.name])
        except Exception:
            pass

        # Téléversement de la vidéo sur Supabase
        supabase.storage.from_(BUCKET_NAME).upload(video_file.name, temp_file_path)
        video_url = supabase.storage.from_(BUCKET_NAME).get_public_url(video_file.name)

        user_name = st.text_input("Ton prénom / pseudo")
        if st.button("Enregistrer le pitch") and user_name:
            # Enregistrement des données dans Supabase
            data = {
                "user_name": user_name,
                "video_url": video_url,
                "transcription": transcription,
                "disc_profile": profile,
                "ai_feedback": feedback
            }
            supabase.table("pitchs").insert(data).execute()
            st.success("Pitch et coaching sauvegardés avec succès !")
        elif st.button("Enregistrer le pitch") and not user_name:
            st.warning("Merci d’ajouter un prénom ou pseudo.")
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
