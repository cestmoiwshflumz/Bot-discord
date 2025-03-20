import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Vérifier que le token est bien chargé
if TOKEN is None:
    raise ValueError("❌ Le token est introuvable ! Vérifie ton fichier .env.")

# Configurer les intentions du bot
intents = discord.Intents.default()
intents.message_content = True

# Créer un bot en mode application commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Événement : Quand le bot est prêt
@bot.event
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()  # Forcer la synchro des slash commands
        print(f"✅ {bot.user} est connecté ! {len(synced)} commandes synchronisées.")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

# Commande Slash : /hello
@bot.tree.command(name="hello", description="Dit bonjour !")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Salut ! Je suis en ligne 🚀", ephemeral=False)

# Lancer le bot
bot.run(TOKEN)
