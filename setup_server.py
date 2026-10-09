import os, asyncio, discord
STRUCT = [
 ("📌 START HERE", ["welcome","rules","announcements","introductions"]),
 ("📰 DAILY FEED", ["ai-pharma-daily","frontier-tech"]),
 ("💬 COMMUNITY", ["general","papers-and-preprints","lit-bot"]),
 ("🎓 PHD PATH", ["phd-applications","sop-and-cv-review","funding-and-fee-waivers","interviews"]),
 ("💼 CAREERS", ["jobs-ireland-eu","jobs-us","grad-programmes"]),
 ("🧑‍💻 LEARN TO CODE", ["python-for-bio","ml-for-biology","project-showcase"]),
 ("🛠 STAFF", ["mod-log"]),
]
READONLY = {"welcome","rules","announcements","ai-pharma-daily","frontier-tech"}
RULES = """**Rules**
1. Be respectful. No harassment, hate speech, or discrimination.
2. No medical advice. Nothing here replaces a doctor or pharmacist. Do not ask for diagnoses or dosing.
3. AI outputs can be wrong. Always check the cited sources before relying on any bot summary.
4. No spam or unsolicited DMs. Self-promotion only in #project-showcase.
5. Do not share confidential, proprietary, or patient data, or anything under NDA.
6. Respect academic integrity. We review and discuss work, we do not write your assignments or applications for you.
7. Share job and PhD posts with a source link.
8. Follow Discord's Terms of Service and Community Guidelines. You must meet the minimum age for Discord in your country.
Mods may remove content or members that break these rules."""
WELCOME = """Welcome to AI Pharma & PhD Hub! 🧬🤖
A community for pharma and biotech students, bio-AI PhD applicants, and early-career scientists moving into AI for drug discovery.

Start here:
1. Read {rules}
2. Say hi in {intro}: your field, where you are, and what you're aiming for
3. Check {daily} for today's news
4. Try /lit <target> in {lit} (e.g. /lit KRAS G12C) for a cited multi-model literature summary

Run by Xiaofan, a final-year Pharmaceutical Science student at TU Dublin who is learning to code and applying to bio-AI PhDs. We're building this in public, so feedback is welcome!"""
client = discord.Client(intents=discord.Intents.default())
@client.event
async def on_ready():
    g = client.guilds[0]; created=[]
    ch = {c.name:c for c in g.text_channels}
    cats = {c.name:c for c in g.categories}
    for cname, chans in STRUCT:
        cat = cats.get(cname) or await g.create_category(cname); 
        if cname not in cats: created.append("category "+cname); cats[cname]=cat
        for n in chans:
            if n in ch:
                if ch[n].category is None: await ch[n].edit(category=cat)
                continue
            ow = {}
            if n in READONLY:
                ow = {g.default_role: discord.PermissionOverwrite(send_messages=False), g.me: discord.PermissionOverwrite(send_messages=True)}
            if n=="mod-log":
                ow = {g.default_role: discord.PermissionOverwrite(view_channel=False), g.me: discord.PermissionOverwrite(view_channel=True)}
            ch[n] = await cat.create_text_channel(n, overwrites=ow); created.append("#"+n)
    posted=[]
    async def post_once(c, text, marker):
        async for m in c.history(limit=50):
            if m.author.id==client.user.id and marker in m.content: return
        await c.send(text, allowed_mentions=discord.AllowedMentions.none()); posted.append("#"+c.name)
    await post_once(ch["rules"], RULES, "**Rules**")
    await post_once(ch["welcome"], WELCOME.format(rules=ch["rules"].mention,intro=ch["introductions"].mention,daily=ch["ai-pharma-daily"].mention,lit=ch["lit-bot"].mention), "Welcome to AI Pharma")
    print("CREATED", created); print("POSTED", posted); await client.close()
client.run(os.environ["DISCORD_BOT_TOKEN"], log_handler=None)
