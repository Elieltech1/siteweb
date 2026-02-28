import asyncio
import logging
import gspread
from google.oauth2.service_account import Credentials

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.helpers import escape_markdown

# ================== CONFIG ==================
TOKEN = "8553391305:AAEsnHCVyGc7ejIjS0OwBfWbikvHWg9aWn0"

# ---------- Boutons ----------
BTN_BACK = "🔙 Retour"
BTN_SERVICES = "🎁 Services Surprise"
BTN_CONTACT = "📞 Nous contacter"
BTN_ESPACE_MEMBRE = "🛡️ Espace Membre"
BTN_MEMOIRES = "📚 Mémoires"
BTN_THESES = "🎓 Thèses"
BTN_ARCHIVES = "🗂️ Archives Académiques"
BTN_TP_TD = "📝 TP / TD"
BTN_FORMATIONS = "🎯 Formations"
BTN_DEVENIR_MEMBRE = "✨ Accéder / Devenir Membre"

PROMOTIONS = [
    ["Préparatoire", "BAC 1"],
    ["BAC 2", "BAC 3"],
    ["Master 1", "Master 2"],
    [BTN_SERVICES]
]

# ---------------- Départements pour BAC2, BAC3, Master2 ----------------
DEPARTEMENTS = [
    ["Chimie Industrielle", "Mines et Grands Travaux"],
    ["Métallurgie", "Electromécanique"],
    [BTN_BACK]
]

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)

# ================== GOOGLE SHEET ==================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

sheet_courses = client.open("PolytechAcademiaCourses").sheet1

try:
    sheet_members = client.open("PolytechAcademiaCourses").worksheet("Membres")
except gspread.exceptions.WorksheetNotFound:
    sheet_members = client.open("PolytechAcademiaCourses").add_worksheet(
        title="Membres", rows="100", cols="2"
    )
    sheet_members.append_row(["user_id", "nom"])

def load_data(sheet):
    return sheet.get_all_records()

def is_member(user_id):
    membres = load_data(sheet_members)
    return any(str(user_id) == str(m["user_id"]) for m in membres)

# ================== COMMANDS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    menu_principal = PROMOTIONS.copy()
    menu_principal.append([BTN_ESPACE_MEMBRE])  # Toujours visible

    await update.message.reply_text(
        "🎓 *Bienvenue sur PolytechAcademiaBot*\n\n"
        "Plateforme d’accès aux *cours, mémoires et ressources académiques*.\n\n"
        "🚀 *Développé par Polytech Academia Startup*\n"
        "Innovation • Partage du savoir • Automatisation\n\n"
        "📚 *Choisissez votre promotion* 👇",
        reply_markup=ReplyKeyboardMarkup(menu_principal, resize_keyboard=True),
        parse_mode="Markdown"
    )

# ================== SERVICES ==================
async def services_menu(update: Update):
    menu = ReplyKeyboardMarkup([[BTN_CONTACT], [BTN_BACK]], resize_keyboard=True)
    await update.message.reply_text(
        "🎁 *NOS SERVICES*\n\n"
        "🖨 *Impression & Reliure professionnelle*\n"
        "- Rapports de stage\n"
        "- Mémoires & TFC\n"
        "- Supports de cours et documents officiels\n"
        "👉 *400 FC par page (reliure incluse)*\n\n"

        "💻 *Installation de logiciels académiques*\n"
        "Nous mettons à votre disposition des logiciels *selon votre département* 👇\n\n"

        "⚙️ *Génie Chimique / Industriel*\n"
        "- Aspen Plus\n"
        "- ChemLab\n"
        "- METSIM\n\n"

        "⛏ *Génie Minier / Géologie*\n"
        "- Surpac\n"
        "- Datamine\n"
        "- ArcGIS\n\n"

        "🏗 *Génie Civil*\n"
        "- AutoCAD\n"
        "- Robot Structural Analysis\n"
        "- ETABS\n\n"

        "⚡ *Génie Électrique & Informatique*\n"
        "- MATLAB\n"
        "- Proteus\n"
        "- Cisco Packet Tracer\n\n"

        "🔧 *Génie Mécanique*\n"
        "- SolidWorks\n"
        "- AutoCAD Mechanical\n\n"

        "📌 *Besoin d’un logiciel spécifique ou d’un accompagnement ?*\n"
        "👉 Cliquez sur *« Nous contacter »* pour échanger directement avec notre équipe.",
        reply_markup=menu,
        parse_mode="Markdown"
    )

async def contact_menu(update: Update):
    await update.message.reply_text(
        "📞 *Contact*\n\n"
        "📧 elielngoyme@yahoo.com\n"
        "📱 WhatsApp : +243977417619",
        parse_mode="Markdown"
    )

# ================== DOCUMENTS ==================
async def send_documents(update: Update, promotion: str, departement: str):
    data = load_data(sheet_courses)
    docs = [
        row for row in data
        if row["promotion"].lower() == promotion.lower()
        and (row["departement"].lower() == departement.lower() if departement else True)
    ]

    if not docs:
        await update.message.reply_text("❌ Aucun document trouvé.")
        return

    for doc in docs:
        cours = escape_markdown(doc["cours"], version=2)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Télécharger", url=doc["lien"])]
        ])
        await update.message.reply_text(
            f"📄 *{cours}*",
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        await asyncio.sleep(0.3)

# ================== ESPACE MEMBRE ==================
async def espace_membre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    membre = is_member(user_id)

    menu = [
        [BTN_MEMOIRES, BTN_THESES],
        [BTN_ARCHIVES, BTN_TP_TD],
        [BTN_FORMATIONS],
        [BTN_DEVENIR_MEMBRE] if not membre else [],
        [BTN_BACK]
    ]

    await update.message.reply_text(
        "🛡️ *ESPACE MEMBRE*\n\n"
        "Accès réservé aux membres Premium c'est dans le but de soutenir cette ouvre.\n\n"
        f"🆔 *Votre ID Telegram :* `{user_id}`\n\n"
        "👉 Cliquez sur *Nous contacter* si besoin.",
        reply_markup=ReplyKeyboardMarkup([row for row in menu if row], resize_keyboard=True),
        parse_mode="Markdown"
    )

# ================== FORMATIONS ==================
async def formations_menu(update: Update):
    user_id = update.effective_user.id
    membre = is_member(user_id)

    # Afficher toutes les formations avec description
    formations = [
        ("📊 Excel Avancé", "Fonctions avancées, tableaux croisés dynamiques, macros."),
        ("💻 Aspen Plus", "Modélisation et simulation de procédés chimiques."),
        ("🏗 AutoCAD", "Conception 2D et 3D de plans techniques."),
        ("⚡ MATLAB", "Programmation scientifique et calcul numérique."),
        ("🔧 SolidWorks", "Modélisation mécanique 3D."),
        ("⛏ Surpac", "Logiciel pour modélisation de gisements miniers."),
    ]

    text = "🎯 *FORMATIONS DISPONIBLES*\n\n"
    for f in formations:
        text += f"{f[0]} : {f[1]}\n\n"

    # Boutons
    if membre:
        menu = [[BTN_BACK]]  # Membre → juste retour
    else:
        menu = [[BTN_DEVENIR_MEMBRE], [BTN_BACK]]  # Non membre → bouton devenir membre + retour

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True),
        parse_mode="Markdown"
    )


# ================== MESSAGE HANDLER ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data
    user_id = update.effective_user.id

    # Menus principaux
    if text == BTN_SERVICES:
        await services_menu(update)
        return

    if text == BTN_CONTACT:
        await contact_menu(update)
        return

    if text == BTN_BACK:
        await start(update, context)
        return

    if text == BTN_ESPACE_MEMBRE:
        await espace_membre(update, context)
        return

    if text == BTN_FORMATIONS:
        await formations_menu(update)
        return

    # Promotions
    if text in ["Préparatoire", "BAC 1"]:
        user_data["promotion"] = text
        menu_prepa = [[BTN_ESPACE_MEMBRE], [BTN_BACK]]
        await send_documents(update, text, "")
        await update.message.reply_text(
            "🛡️ Pour soutenir cette Ouvre Accédez à l’Espace Membre et si vous voulez du contenu Premium",
            reply_markup=ReplyKeyboardMarkup(menu_prepa, resize_keyboard=True)
        )
        return

    if text in ["BAC 2", "BAC 3", "Master 1"]:
        user_data["promotion"] = text
        menu_dept = DEPARTEMENTS.copy()
        menu_dept.append([BTN_ESPACE_MEMBRE])
        await update.message.reply_text(
            "Choisissez votre département 👇",
            reply_markup=ReplyKeyboardMarkup(menu_dept, resize_keyboard=True)
        )
        return

    # Départements
    if text in [d for row in DEPARTEMENTS[:-1] for d in row]:
        await send_documents(update, user_data.get("promotion", ""), text)
        await update.message.reply_text(
            "🛡️ Accédez à l’Espace Membre",
            reply_markup=ReplyKeyboardMarkup([[BTN_ESPACE_MEMBRE], [BTN_BACK]], resize_keyboard=True)
        )
        return

    # Espace membre interne
    if text in [BTN_MEMOIRES, BTN_THESES, BTN_ARCHIVES, BTN_TP_TD]:
        if not is_member(user_id):
            await espace_membre(update, context)
            return
        await update.message.reply_text(f"🔹 Contenu Premium : {text}")

    if text == BTN_DEVENIR_MEMBRE:
        await update.message.reply_text(
            f"✨ Pour devenir membre, veuillez nous envoyer votre *ID Telegram* : `{user_id}`\n"
            "Nous vous ajouterons manuellement dans l'espace membre via notre Google Sheet.",
            reply_markup=ReplyKeyboardMarkup([[BTN_CONTACT], [BTN_BACK]], resize_keyboard=True),
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text("⛔ les Support de cette promotions seront dispobles ici tres bientot.")

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 PolytechAcademiaBot démarré")
    app.run_polling()

if __name__ == "__main__":
    main()
