from utils import send_message

# ================================
# ⚠️ DÉMARRER LE MODE PROBLÈME
# ================================
def handle_problem(user_id):
    """
    Première étape quand l'utilisateur signale un problème.
    On lui demande d'expliquer ce qui ne fonctionne pas.
    """
    send_message(
        user_id,
        "⚠️ من فضلك اشرح لنا مشكلتك بالتفصيل (مثلًا : الحساب لا يعمل، يطلب كود، تم تسجيل الخروج...) 🙏"
    )


# ================================
# 💬 TRAITER LES RÉPONSES CLIENT
# ================================
def process_problem_text(user_id, text):
    """
    Cette fonction peut être appelée plus tard si tu veux
    automatiser la prise en charge des réponses clients
    (ex : envoi automatique au support admin).
    """

    # Tu peux ici envoyer une notification à l’admin Messenger
    # Exemple :
    ADMIN_ID = "1234567890"  # <-- remplace par ton ID Facebook admin
    send_message(
        ADMIN_ID,
        f"📩 Nouveau signalement client :\n\n{text}\n\n👤 ID utilisateur : {user_id}"
    )

    # Confirmer au client qu'on a bien reçu son message
    send_message(
        user_id,
        "✅ تم استلام مشكلتك، سنتواصل معك في أقرب وقت ممكن 🙏"
    )
