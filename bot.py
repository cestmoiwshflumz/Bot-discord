import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import spotify
import soundcloud

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1351998576548515900  # Remplace par l'ID du canal Discord

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} est connecté !")
    check_spotify.start()  # Lancer la vérification automatique
    check_soundcloud.start()

# Commande Slash : /last_track
@bot.tree.command(name="last-spotify", description="Affiche la dernière sortie de l'artiste suivi")
async def last_track(interaction: discord.Interaction):
    release = spotify.get_latest_release()  # On utilise l'ID d'artiste déjà défini dans spotify.py
    if release:
        embed = discord.Embed(
            title=release["name"],
            url=release["url"],
            description=f"🗓 **Date de sortie** : {release['release_date']}",
            color=discord.Color.green()
        )
        embed.set_image(url=release["cover"])  # Ajouter la cover
        embed.set_footer(text="Écoute sur Spotify", icon_url="https://cdn-icons-png.flaticon.com/512/2111/2111624.png")

        # Ajouter un aperçu audio si disponible
        if "preview" in release and release["preview"]:
            embed.add_field(name="🎧 Aperçu", value=f"[Écouter l'extrait]({release['preview']})", inline=False)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Aucune nouvelle sortie trouvée.", ephemeral=True)


# Vérification automatique toutes les 5 minutes
@tasks.loop(minutes=5)
async def check_spotify():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Erreur : Canal introuvable.")
        return

    new_release = spotify.check_for_new_release()
    if new_release:
        embed = discord.Embed(
            title="🚨 NOUVELLE SORTIE !",
            description=f"🎵 **{new_release['name']}** est maintenant disponible !\n\n🔗 [Écouter sur Spotify]({new_release['url']})",
            color=discord.Color.blue()
        )
        embed.set_image(url=new_release["cover"])  # Ajouter la cover
        embed.set_footer(text="Écoute sur Spotify", icon_url="https://cdn-icons-png.flaticon.com/512/2111/2111624.png")

        # Ajouter un aperçu audio si disponible
        if new_release["preview"]:
            embed.add_field(name="🎧 Aperçu", value=f"[Écouter l'extrait]({new_release['preview']})", inline=False)

        await channel.send(embed=embed)


@bot.tree.command(name="last-soundcloud", description="Affiche le dernier son de l'artiste sur SoundCloud")
async def last_sound(interaction: discord.Interaction):
    latest_sound = soundcloud.get_latest_sound()
    if latest_sound:
        embed = discord.Embed(
            title=latest_sound["title"],
            url=latest_sound["url"],
            description=f"🗓 **Date de sortie** : {latest_sound['published']}",
            color=discord.Color.orange()
        )
        if latest_sound["image"]:  # ✅ Ajout de la cover
            embed.set_image(url=latest_sound["image"])
        embed.set_footer(text="Écoute sur SoundCloud", icon_url="https://cdn-icons-png.flaticon.com/512/3955/3955076.png")

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Aucune nouvelle sortie trouvée.", ephemeral=True)

@tasks.loop(minutes=5)
async def check_soundcloud():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Erreur : Canal introuvable.")
        return

    new_sound = soundcloud.check_for_new_sound()
    if new_sound:
        embed = discord.Embed(
            title="🚨 NOUVEAU SON SUR SOUNDCLOUD !",
            description=f"🎵 **{new_sound['title']}** vient de sortir !\n\n🔗 [Écouter sur SoundCloud]({new_sound['url']})",
            color=discord.Color.orange()
        )
        if new_sound["image"]:
            embed.set_thumbnail(url=new_sound["image"])
        await channel.send(embed=embed)


bot.run(TOKEN)
