import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# 参加データ形式: { "2025-06-01": [ {"name": "田中", "title": "機械学習について"}, ... ] }
session_data = {}
session_dates = []

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Botが起動しました: {bot.user.name}")

# /create
@tree.command(name="create", description="発表会の日時を作成します（例：/create 2025-06-01）")
@app_commands.describe(date="発表会の日付 (例: 2025-06-01)")
async def create(interaction: discord.Interaction, date: str):
    if date in session_dates:
        await interaction.response.send_message(f"{date} はすでに作成されています。")
        return
    session_dates.append(date)
    session_data[date] = []
    await interaction.response.send_message(f"✅ {date} の発表会を作成しました。")

# /req
@tree.command(name="req", description="発表会に参加希望を出します（名前と内容を入力）")
@app_commands.describe(name="参加者の名前", title="発表会で話す内容などのタイトル")
async def req(interaction: discord.Interaction, name: str, title: str):
    if not session_dates:
        await interaction.response.send_message("まだ作成された発表会の日付がありません。", ephemeral=True)
        return

    view = View(timeout=None)
    added = False

    for date in sorted(session_dates):  # ← 日付順にソート
        if len(session_data.get(date, [])) >= 2:
            continue

        button = Button(label=date, style=discord.ButtonStyle.primary)

        async def callback(interaction_button: discord.Interaction, d=date, n=name, t=title):
            if any(entry["name"] == n for entry in session_data[d]):
                await interaction_button.response.send_message(f"{d} の発表会にはすでに参加済みです。", ephemeral=True)
            else:
                session_data[d].append({"name": n, "title": t})
                await interaction_button.response.send_message(f"✅ {n} さんが {d} の発表会に参加登録しました！\n📝 タイトル: {t}")

        button.callback = callback
        view.add_item(button)
        added = True

    if added:
        await interaction.response.send_message(f"🎤 {name} さん、発表内容「{title}」で参加したい日付を選んでください：", view=view, ephemeral=True)
    else:
        await interaction.response.send_message("参加可能な日付（空きあり）はありません。", ephemeral=True)

# /can
@tree.command(name="can", description="発表会の参加をキャンセルします")
@app_commands.describe(name="キャンセルする名前", date="発表会の日付 (例: 2025-06-01)")
async def can(interaction: discord.Interaction, name: str, date: str):
    if date in session_data:
        for entry in session_data[date]:
            if entry["name"] == name:
                session_data[date].remove(entry)
                await interaction.response.send_message(f"🚫 {name} さんの {date} の発表会参加をキャンセルしました。")
                return
    await interaction.response.send_message(f"{date} の発表会には {name} さんは参加していません。")

# /list
@tree.command(name="list", description="各日付の参加者一覧を表示します")
async def list_participants(interaction: discord.Interaction):
    if not session_data:
        await interaction.response.send_message("まだ参加希望者はいません。")
        return

    message = "**📅 参加者一覧:**\n"
    for date in sorted(session_data.keys()):
        entries = session_data[date]
        if entries:
            entry_text = "\n".join([f"- {e['name']}「{e['title']}」" for e in entries])
            message += f"**{date}**:\n{entry_text}\n"
        else:
            message += f"**{date}**: （参加者なし）\n"

    await interaction.response.send_message(message)

# /reset
@tree.command(name="reset", description="すべての予定と参加希望をリセットします（管理者用）")
async def reset(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⚠️ このコマンドは管理者のみ実行できます。", ephemeral=True)
        return
    session_data.clear()
    session_dates.clear()
    await interaction.response.send_message("🗑️ すべての予定と参加希望をリセットしました。")

# トークン（安全な方法で管理してください）
bot.run("MTM3NjE2ODcwMjc4MDYzNzI5NA.Gm8-40.osa6XgIITF7o6aa7P3xYDR2WtF0woad8weo4Lk")
