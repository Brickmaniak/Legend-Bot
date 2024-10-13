import discord
from discord import app_commands
from discord.ext import commands,tasks
import random
import json
import datetime

intents = discord.Intents().all()
bot = commands.Bot(command_prefix = "+", intents=intents)
status = ["+ping",
         "+pileouface",
         "+help",
         "+serverInfo",
         "+devconsole",
         "Coucou!",
	 "+chinese",
         "+blague",
         "+giffle",
         "+calin",
         "+chatouiller",
         "+nourrir",
         "+ticket",
         "En développement!"]

intents.message_content = True
intents.members = True
intents.voice_states = True
raid_detection_threshold = 10
raid_detection_window = 60
raid_cooldown_window = 300

join_timestamps = []
auto_kick_enabled = True
raid_in_progress = False

@bot.event
async def on_ready():
    print(f"{bot.user.name} est pret !")
    changeStatus.start()

@bot.command(help="Ne pas utiliser -_-",)
@commands.has_permissions(administrator=True)
async def start(ctx, secondes = 3):
    changeStatus.change_interval(seconds = secondes)

@tasks.loop(seconds = 3)
async def changeStatus():
    game = discord.Game(random.choice(status))
    await bot.change_presence(status = discord.Status, activity = game)

@bot.command(help="Affiche le ping du bot",)
async def ping(ctx):
    await ctx.reply(f"Pong! Latence : {round(bot.latency * 1000)}ms !")

@bot.command(help="Joue a pile ou face",)
async def pileouface(ctx):
    await ctx.reply(random.choices(["Pile", "Face"]))

@bot.command(help="Propriétés du serveur")
async def serverinfo(ctx):
    server = ctx.guild
    numberOfTextChannels = len(server.text_channels)
    numberOfVoiceChannels = len(server.voice_channels)
    numberOfPersons = server.member_count
    serverName = server.name
    message = f"Le serveur **{serverName}** compte **{numberOfPersons}** membres \nIl possède **{numberOfTextChannels}** salons textuels et **{numberOfVoiceChannels}** salons vocaux"
    await ctx.reply(message)

@bot.command(help="Parler dans la console du bot",)
async def devconsole(ctx, *texte):
    print(" ".join(texte))
    await ctx.message.delete()

@bot.command(name='antiraid-disable')
@commands.has_permissions(manage_messages=True)
async def disable_antiraid(ctx):
    global auto_kick_enabled
    auto_kick_enabled = False
    await ctx.reply('Antiraid désactivé.')

@bot.command(name='antiraid-enable')
@commands.has_permissions(manage_messages=True)
async def enable_antiraid(ctx):
    global auto_kick_enabled
    auto_kick_enabled = True
    await ctx.reply('Antiraid activé')

@bot.event
async def on_member_join(member):
    global raid_in_progress
    join_timestamps.append(datetime.datetime.now())
    if len(join_timestamps) > raid_detection_threshold:
        recent_joins = [ts for ts in join_timestamps if (datetime.datetime.now() - ts).total_seconds() < raid_detection_window]
        if len(recent_joins) > raid_detection_threshold:
            auto_kick_enabled = True
            raid_in_progress = True
            await auto_kick_members(member)
        else:
            auto_kick_enabled = False
            raid_in_progress = False
    else:
        auto_kick_enabled = False
        raid_in_progress = False

    join_timestamps = [ts for ts in join_timestamps if (datetime.datetime.now() - ts).total_seconds() < raid_detection_window + raid_cooldown_window]

    if raid_in_progress and len([ts for ts in join_timestamps if (datetime.datetime.now() - ts).total_seconds() < raid_cooldown_window]) < raid_detection_threshold:
        auto_kick_enabled = False
        raid_in_progress = False

async def auto_kick_members(member):
    for m in member.guild.members:
        if m.joined_at > datetime.datetime.now() - datetime.timedelta(seconds=raid_detection_window):
            await m.kick(reason='Raid détecté')

@bot.command(help="Parler via le bot",)
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, saymessage):
    await ctx.send(saymessage)
    await ctx.message.delete()
    print(f"{ctx.author} à envoyé un message via le bot: {saymessage}.")

@bot.command(help="Expulser un membre",)
@commands.has_permissions(manage_messages=True)
async def kick(ctx, user : discord.User, *reason):
	reason = " ".join(reason)
	await ctx.guild.kick(user, reason = reason)
	await ctx.reply(f"{user} à été expulsé.")

@bot.command(help="Bannir un membre",)
@commands.has_permissions(manage_messages=True)
async def ban(ctx, user : discord.User, *reason):
	reason = " ".join(reason)
	await ctx.guild.ban(user, reason = reason)
	await ctx.reply(f"{user} à été banni pour la raison suivante : {reason}.")

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.reply("Mmmmmmh, j'ai bien l'impression que cette commande n'existe pas :/")

	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("Il manque un argument. (ex. +commande argument)")
	elif isinstance(error, commands.MissingPermissions):
		await ctx.reply("Vous n'avez pas les permissions pour éxécuter cette commande.")
	elif isinstance(error, commands.CheckFailure):
		await ctx.reply("Oups vous ne pouvez pas utiliser cette commande.")
	if isinstance(error.original, discord.Forbidden):
		await ctx.reply("Oups, je n'ai pas les permissions nécéssaires pour éxécuter cette commmande")

@bot.command(help="Convert. Caractères FR en caractères chinois")
async def chinese(ctx, *text):
	chineseChar = "丹书匚刀巳下呂廾工丿片乚爪冂口尸Q尺丂丁凵V山乂Y乙"
	chineseText = []
	await ctx.message.delete()
	for word in text:
		for char in word:
			if char.isalpha():
				index = ord(char) - ord("a")
				transformed = chineseChar[index]
				chineseText.append(transformed)
			else:
				chineseText.append(char)
		chineseText.append(" ")
	await ctx.send("".join(chineseText))

@bot.event
async def on_member_join(member):
    try:
        welcome_message = (
            f"Bienvenue sur **Légende urbaine**, **{member.mention}** ! "
        )
        await member.send(welcome_message)
        print(f'Message de bienvenue envoyé à {member.name}')
    except discord.Forbidden:
        print(f'Impossible d\'envoyer un message à {member.name}')

@bot.command(help="Effacer un nombre de messages précis", aliases=['purge', 'delete'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 100):
    await ctx.channel.purge(limit=amount + 1)

@bot.command(help="Ouvrir un ticket")
async def ticket(ctx, *, raison):
        category = discord.utils.get(ctx.guild.categories, name='🎟tickets🎟')
        if category is None:
            category = await ctx.guild.create_category('🎟tickets🎟')

        ticket_channel = await category.create_text_channel(f'ticket-{ctx.author.name}')
        staff_role = discord.utils.get(ctx.guild.roles, name="Staff")
        await ticket_channel.set_permissions(discord.utils.get(ctx.guild.roles, name="Staff"), send_messages=True)
        await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await ctx.reply(f'Votre ticket a bien été créé dans {ticket_channel.mention}')
        await ticket_channel.send(f"{staff_role.mention} Nouveau ticket créé par {ctx.author.mention} pour la raison: {raison} !", mention_author=False)
        
@bot.command(help="Vérouille un salon.",)
@commands.has_permissions(manage_channels = True)
async def lock(ctx):
    await ctx.channel.set_permissions(discord.utils.get(ctx.guild.roles, name="Staff"), send_messages=True)
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.reply( ctx.channel.mention + " **est vérouillé 🔒.**")
    
@bot.command(help="Dévérouille un salon",)
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.reply(ctx.channel.mention + " **est dévérouillé 🔓.**")

@bot.command(help="Warn un membre",)
@commands.has_permissions(manage_messages=True)
async def warn(ctx, user : discord.Member, *, reason=None):
    warn_role = discord.utils.get(ctx.guild.roles, name="Warned")
    if not warn_role:
        warn_role = await ctx.guild.create_role(name="Warned")
    await user.add_roles(warn_role)
    await ctx.reply(f"{user.mention} a été warn pour la raison suivante : {reason}.")

@bot.command(help="Enlève un warn à un membre",)
@commands.has_permissions(manage_messages=True)
async def unwarn(ctx, user : discord.Member):
    warn_role = discord.utils.get(ctx.guild.roles, name="Warned")
    await user.remove_roles(warn_role)
    await ctx.reply(f"{user.mention} a été unwarn.")

@bot.command(help="Mute un membre",)
@commands.has_permissions(manage_messages=True)
async def mute(ctx, user : discord.Member, *, reason=None):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False)
    await user.add_roles(mute_role)
    await ctx.reply(f"{user.mention} a été mute pour la raison suivante : {reason}.")

@bot.command(help="Unmute un membre",)
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, user : discord.Member):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await user.remove_roles(mute_role)
    await ctx.reply(f"{user.mention} a été unmute.")

@bot.command(help="Ferme un ticket",)
@commands.has_permissions(manage_messages=True)
async def closeticket(ctx, channel: discord.TextChannel):
    if channel.category.name == '🎟tickets🎟':
        await channel.delete()
        await ctx.reply(f"Le ticket {channel.name} a été fermé.")
    else:
        await ctx.reply("Ce salon n'est pas un ticket.")

@bot.command(help="Blague aléatoire (Parmis plus de 50 blagues)")
async def blague(ctx):
    blagues = [
        "C'est l'histoire du p’tit dej, tu la connais ? \n ||Pas de bol.||",
        "Que demande un footballeur à son coiffeur ? \n ||La coupe du monde s’il vous plait.||",
        "Comment s'appelle le cul de la Schtroumpfette ? \n ||Le Blu-ray.||",
        "C'est quoi une chauve-souris avec une perruque ? \n ||Une souris.||",
        "Que dit un escargot quand il croise une limace ? \n ||Oh un naturiste.||",
        "Pourquoi les canards sont toujours à l'heure ? \n ||Parce qu’ils sont dans l’étang.||",
        "Qu'est-ce qui est dur, blanc, avec le bout rouge, et qui sent la pisse ? \n ||Une borne kilométrique.||",
        "Que fait un crocodile quand il rencontre une superbe femelle ? \n ||Il Lacoste.||",
        "C'est quoi un petit pois avec une épée face à une carotte avec une épée ? \n ||Un bon duel.||",
        "Pourquoi les pêcheurs ne sont pas gros ? \n ||Parce qu’ils surveillent leur ligne.||",
        "Tu connais la blague de la chaise? \n ||Elle est tellement longue.||",
        "C'est l'histoire d'un papier qui tombe à l'eau. \n ||Il crie Au secours ! J’ai pas pied !||",
        "Que fait une fraise sur un cheval ? \n ||Tagada Tagada.||",
        "C'est l'histoire de 2 patates qui traversent la route. L’une d’elles se fait écraser. \n ||L’autre dit : Oh purée !||",
        "Quel est le crustacé le plus léger de la mer ? \n ||La palourde||",
        "Une fesse gauche rencontre une fesse droite : \n ||Tu ne trouves pas que ça pue dans le couloir ?||",
        "Qu'est-ce qui n'est pas un steak ? \n ||Une pastèque.||",
        "C'est l'histoire d'un poil. \n ||Avant il était bien, maintenant il est pubien.||",
        "Qu'est-ce qui fait toin toin ? \n ||Un tanard.||",
        "Pourquoi un chasseur emmène-t-il son fusil aux toilettes ? \n ||Pour tirer la chasse.||",
        "Où va Messi quand il se blesse ? \n ||À la pharmessi.||",
        "Quelle est la mamie qui fait peur aux voleurs ? \n ||Mamie Traillette.||",
        "Comment appelle-t-on un chien qui n'a pas de pattes ? \n ||On ne l’appelle pas, on va le chercher…||",
        "Qu'est-ce qui est vert, se déplace sous l'eau, et fait buzzzzz ? \n ||Un chou marin ruche.||",
        "Comment appelle-t-on un bébé éléphant prématuré ? \n ||Un éléphant tôt.||",
        "Pourquoi les vaches ferment-elles les yeux pendant la traite de lait ? \n ||Pour faire du lait concentré.||",
        "Un mec rentre dans un café. \n ||Et plouf.||",
        "C'est l'histoire d'un mec qui a 5 pénis. \n ||Son slip lui va comme un gant.||",
        "Que dit un Italien pour dire au revoir ? \n ||Pasta la vista||",
        "Que dit un chihuahua japonais pour dire bonjour ? \n ||Konichihuahua||",
        "Avec quoi ramasse-t-on la papaye ? \n ||Avec une foufourche.||",
        "C'est l'histoire d'une brioche qui n'allait jamais aux sports d'hiver \n ||Parce qu’elle ne savait Pasquier.||",
        "Comment fait un chat pour s'essuyer les fesses quand il fait caca dans le désert ? \n ||Tu donnes ta langue au chat ?||",
        "C'est l'histoire d'un putois qui rencontre un autre putois. \n ||Il lui dit : tu pues toi||",
        "Qu'est-ce qu'un bossu sans bras ni jambes ? \n ||Une madeleine.||",
        "C'est l'histoire d'un flamant rose. \n ||Un jour il a pris son pied, et il est tombé.||",
        "Pourquoi les girafes ont-elles un long cou ? \n ||Parce qu’elles puent du cul.||",
        "Qu'est-ce qui est petit, vert, et qui fait très très peur ? \n ||Un petit pois avec un bazooka.||",
        "Que dit un informaticien quand il s'ennuie ? \n ||Je me fichier.||",
        "Qu'est-ce qu'un canif ? \n ||Un petit fien.||",
        "Qu'est-ce qui est jaune et qui fait crac crac ? \n ||Un poussin qui mange des chips.||",
        "Comment savoir quand un sapin est en colère ? \n ||Il a les boules.||",
        "Que prend un éléphant dans un bar ? \n ||Beaucoup de place.||",
        "C'est l'histoire d'un têtard. Il croyait qu'il était tôt. \n ||Mais en fait il est têtard.||",
        "Pourquoi le lapin est bleu ? \n ||Parce qu’on l’a peint.||",
        "Comment appelle-t-on un lapin sourd ? \n ||LAAAAAAPIIIIIIIINNNNNNN!!!!!!||",
        "Pourquoi faut-il enlever ses lunettes avant un alcootest ? \n ||Ça fait 2 verres en moins.||",
        "Pourquoi Mickey Mouse ? \n ||Parce que Mario Bros.||",
        "C'est l'histoire d'une mouette qui partage un gâteau \n ||Du coup elle fait mouette mouette.||",
        "Tu connais l'histoire de la feuille ? \n ||Elle déchire.||",
        "Qu'est ce qui est blanc, froid, qui tombe en hiver et qui termine par ard ? \n ||De la neige, connard !||",
        "Pourquoi est-ce que c'est difficile de conduire dans le Nord ? \n ||Parce que les voitures n’arrêtent PAS DE CALER||",
        "Comment est-ce que la chouette sait que son mari fait la gueule ? \n ||Parce qu’HIBOUDE||",
        "Pourquoi est-ce qu'on dit que les Bretons sont tous frères et sœurs ? \n ||Parce qu’ils n’ont Quimper||",
        "Pourquoi est-ce qu'on met tous les crocos en prison ? \n ||Parce que les crocos dealent||",
        "Comment fait-on pour allumer un barbecue breton ? \n ||On utilise des breizh||"
    ]
    await ctx.reply(random.choice(blagues))

@bot.command(help="Un petit calin pour vous")
async def calin(ctx, utilisateur: discord.Member):
    calin_gifs = [
        "https://media1.tenor.com/images/f2805f274471676c96aff2bc9fbedd70/tenor.gif?itemid=7552077",
        "https://c.tenor.com/sX_vDDaD2-4AAAAC/hug-anime.gif",
        "https://64.media.tumblr.com/680b69563aceba3df48b4483d007bce3/tumblr_mxre7hEX4h1sc1kfto1_500.gif",
        "https://media.tenor.com/oQPT1dxDIVQAAAAC/anime-hug.gif",
        "https://media.tenor.com/6w7XKLSqFEUAAAAd/anime-hug.gif",
        "https://gifdb.com/images/high/anime-hug-himouto-umaru-chan-4tqcvdscmhxje0rn.gif",
        "https://media.tenor.com/images/c841c6a0263e5ed16f66d2e8a3e7ab8c/tenor.gif",
        "https://media1.tenor.com/images/6c26cc8164712b7f54980070199b8e7f/tenor.gif?itemid=8833018",
        "https://pa1.narvii.com/5925/bfd5fdfa6132c17a1c768a88536afb0589f7aeb6_hq.gif",
        "https://media.tenor.com/PzIA_wdL3zgAAAAd/wlw-hug.gif",
        "https://usagif.com/wp-content/uploads/gif/anime-hug-25.gif",
        "https://aniyuki.com/wp-content/uploads/2022/06/anime-hugs-aniyuki-18.gif",
        "https://media.tenor.co/images/08de7ad3dcac4e10d27b2c203841a99f/raw",
        "https://media.tenor.co/images/5c35f9a6052b30442d05a855fc76b5de/tenor.gif",
        "https://media1.tenor.com/images/d2a2b216ef3bc74406f661049f937999/tenor.gif?itemid=17023255",
        "https://i.pinimg.com/originals/6d/40/d8/6d40d82e71dc167fd4a247704285fab7.gif",
        "https://media.tenor.com/H5WJ_mYQ49IAAAAd/anime-anime-hug.gif",
        "https://aniyuki.com/wp-content/uploads/2022/06/anime-hugs-aniyuki-49.gif",
        "https://i.pinimg.com/originals/dd/d4/2c/ddd42c994d225d87c0c635ca7cb2c10b.gif",
        "https://usagif.com/wp-content/uploads/gif/anime-hug-26.gif",
        "https://media1.tenor.com/images/969f0f462e4b7350da543f0231ba94cb/tenor.gif?itemid=14246498",
        "https://i.pinimg.com/originals/bb/84/1f/bb841fad2c0e549c38d8ae15f4ef1209.gif",
        "https://aniyuki.com/wp-content/uploads/2022/06/anime-hugs-aniyuki-14.gif",
    ]
    await ctx.reply(f"{ctx.author.mention} fait un calin à {utilisateur.mention}")
    await ctx.send(random.choice(calin_gifs))

@bot.command(help="Une grosse tarte")
async def giffle(ctx, utilisateur: discord.Member):
    giffle_gifs = [
        "https://gifdb.com/images/high/up-close-angry-anime-slap-lf84tjs2sgx8obdr.gif",
        "https://gifdb.com/images/high/yuruyuri-akari-kyoko-anime-slap-fcacgc0edqhci6eh.gif",
        "https://media.tenor.com/XiYuU9h44-AAAAAC/anime-slap-mad.gif",
        "https://gifdb.com/images/high/emotionless-anime-guy-slap-b0qm8xchu44htd1r.gif",
        "https://media1.tenor.com/images/b6d8a83eb652a30b95e87cf96a21e007/tenor.gif?itemid=10426943",
        "https://i.pinimg.com/originals/68/d3/cd/68d3cd90baa448b24aebd79f40efad6c.gif",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/b02c16d5-1b1b-4139-92e6-ca6b3d768d7a/d6wv007-5fbf8755-5fca-4e12-b04a-ab43156ac7d4.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTpmaWxlLmRvd25sb2FkIl0sIm9iaiI6W1t7InBhdGgiOiIvZi9iMDJjMTZkNS0xYjFiLTQxMzktOTJlNi1jYTZiM2Q3NjhkN2EvZDZ3djAwNy01ZmJmODc1NS01ZmNhLTRlMTItYjA0YS1hYjQzMTU2YWM3ZDQuZ2lmIn1dXX0.2djJ-QoGbv3bkgefoX_IrIl5YLe4XlaVlDItlb_D3Ew",
        "https://media.tenor.com/FJsjk_9b_XgAAAAC/anime-hit.gif",
        "https://i.pinimg.com/originals/fb/17/a2/fb17a25b86d80e55ceb5153f08e79385.gif",
        "https://gifdb.com/images/high/intense-fast-grandma-anime-slap-k7kja36j5y6j0ng8.gif",
        "https://i.pinimg.com/originals/1c/8f/0f/1c8f0f43c75c11bf504b25340ddd912d.gif",
        "https://static.wikia.nocookie.net/16345462-4b4c-42d3-b7fb-0b32b43707a3",
        "https://i.pinimg.com/originals/68/de/67/68de679cc20000570e8a7d9ed9218cd3.gif",
        "https://media.tenor.com/1lemb3ZmGf8AAAAC/anime-slap.gif",
        "https://media.tenor.com/8VAgT4nmZ-UAAAAC/slap-anime.gif",
        "https://media1.tenor.com/images/f619012e2ec268d73ecfb89af5a8fb51/tenor.gif?itemid=8562186",
        "https://media1.tenor.com/images/3fd96f4dcba48de453f2ab3acd657b53/tenor.gif?itemid=14358509",
        "https://media.tenor.com/btnM_mAk51kAAAAC/anime-slap.gif",
        "https://media.tenor.com/images/091e0502e5fda1201ee76f5f26eea195/tenor.gif",
        "https://media.tenor.com/Ws6Dm1ZW_vMAAAAM/girl-slap.gif",
        "https://pa1.narvii.com/7440/3639e71f0f54725c3e1d2e2928344bcd2c5133ber1-656-368_00.gif",
        "https://c.tenor.com/E3OW-MYYum0AAAAC/no-angry.gif",
        "https://media.tenor.com/KR4LZDvzVH0AAAAM/slap-anime-slap.gif",
        "https://media1.tenor.com/images/568799ded41fed64cc227b8f467332c0/tenor.gif?itemid=8339033",
    ]
    await ctx.reply(f"{ctx.author.mention} fait une giffle à {utilisateur.mention}")
    await ctx.send(random.choice(giffle_gifs))

@bot.command(help="Guili guiliiii")
async def chatouiller(ctx, utilisateur: discord.Member):
    chatouiller_gifs = [
        "https://i.kym-cdn.com/photos/images/newsfeed/001/011/375/94a.gif",
        "https://media1.tenor.com/images/05a64a05e5501be2b1a5a734998ad2b2/tenor.gif?itemid=11379130",
        "https://pa1.narvii.com/5797/bcd4954b360110b1e64f5d9e0e7e9864acb9f166_hq.gif",
        "https://78.media.tumblr.com/37a7200ecc18c73e9bcaf2f329bdea04/tumblr_inline_ow4ue7Wqwo1u544cj_540.gif",
        "https://media1.tenor.com/images/5cbe2cb77056ef2faf395b26fdece8eb/tenor.gif?itemid=14132818",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/e7e51d35-eadb-4803-87f5-96b733db09e7/d7hyh1y-a20a348d-6503-45bb-b42d-066a9a69acae.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTpmaWxlLmRvd25sb2FkIl0sIm9iaiI6W1t7InBhdGgiOiIvZi9lN2U1MWQzNS1lYWRiLTQ4MDMtODdmNS05NmI3MzNkYjA5ZTcvZDdoeWgxeS1hMjBhMzQ4ZC02NTAzLTQ1YmItYjQyZC0wNjZhOWE2OWFjYWUuZ2lmIn1dXX0.szJGcZWbaC7nWH3nmbkkOVQj4CccsSHaqOHQtK7nSLQ",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/7bbbe46f-5285-46b1-804e-337939538ae7/dbj9hfz-7c5064ae-7edb-4002-8a1f-8f967f20f386.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTpmaWxlLmRvd25sb2FkIl0sIm9iaiI6W1t7InBhdGgiOiIvZi83YmJiZTQ2Zi01Mjg1LTQ2YjEtODA0ZS0zMzc5Mzk1MzhhZTcvZGJqOWhmei03YzUwNjRhZS03ZWRiLTQwMDItOGExZi04Zjk2N2YyMGYzODYuZ2lmIn1dXX0.Xo1VX9eA1Oq9F5XGDAvFVy6yMAc78sVlKXg79aaSKQI",
        "https://i.pinimg.com/originals/fe/a7/9f/fea79fed0168efcaf1ddfb14d8af1a6d.gif",
        "https://media1.tenor.com/images/eaef77278673333265da087f65941e48/tenor.gif?itemid=16574823",
        "https://pa1.narvii.com/6165/cf09ad1f78480c3791fa13200d81242e21dcda5c_hq.gif",
        "https://gifdb.com/images/thumbnail/tickle-touya-yumina-anime-33wow13bs2lv9nb7.gif",
        "https://i.pinimg.com/originals/86/71/4f/86714fe4b8235be518273095b4eacc38.gif",
        "https://i.gifer.com/origin/0c/0c5baf46e82a9094c5e9578742d08834_w200.gif",
        "https://66.media.tumblr.com/26ccd7cd850717a8bd82a6dbc3c21ba2/tumblr_o505jxtnWk1vpbklao10_500.gif",
        "https://64.media.tumblr.com/709c2e0f0f7636b3047664d6ebe28a71/tumblr_mfk79qehz01rt479bo2_500.gif",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/e7e51d35-eadb-4803-87f5-96b733db09e7/d7ipx1k-c46e0bbf-9bb3-4937-a77b-5224c96e5ac9.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTpmaWxlLmRvd25sb2FkIl0sIm9iaiI6W1t7InBhdGgiOiIvZi9lN2U1MWQzNS1lYWRiLTQ4MDMtODdmNS05NmI3MzNkYjA5ZTcvZDdpcHgxay1jNDZlMGJiZi05YmIzLTQ5MzctYTc3Yi01MjI0Yzk2ZTVhYzkuZ2lmIn1dXX0.hJ_YQq8XgmI0GVOHJN_YRYPwOpAekA3n6eXXZwqtcUA",
    ]
    await ctx.reply(f"{ctx.author.mention} fait des chatouilles à {utilisateur.mention}")
    await ctx.send(random.choice(chatouiller_gifs))

@bot.command(help="Nourrir quelqu'un")
async def nourrir(ctx, utilisateur: discord.Member):
    nourrir_gifs = [
        "https://64.media.tumblr.com/5ffb900f8123afd650bcfedd57fd6522/83fe0839dbb07cad-2f/s500x750/55b9e9ca9961660494c8475fc53f1ab907569d2e.gif",
        "https://media.tenor.com/_Wn5KdSnphEAAAAd/anime-feed-anime.gif",
        "https://media.moddb.com/images/groups/1/1/84/kanzashi-eating.gif",
        "https://media.tenor.com/TRuJrALdXnoAAAAC/lycoris-recoil-anime-feed.gif",
        "https://pa1.narvii.com/6313/f84530cfae434391ad7c0443d147d45f34bf5c31_hq.gif",
        "https://i.pinimg.com/originals/9a/42/32/9a4232d1dc9e18b64b7179b439944379.gif",
    ]
    await ctx.reply(f"{ctx.author.mention} nourrit {utilisateur.mention}")
    await ctx.send(random.choice(nourrir_gifs))

@bot.command(help="Envoyer un message privé à un utilisateur")
@commands.has_permissions(manage_messages=True)
async def mp(ctx, utilisateur: discord.Member, *, message):
    await utilisateur.send(message)
    await ctx.reply(f"Message envoyé à {utilisateur.mention}")
    print(f"{ctx.author} a envoyé {message} a {utilisateur}")

@bot.command(name='edit', help='Modifier un message.')
@commands.has_permissions(manage_messages=True)
async def edit_message(ctx, message_id: int, *, new_content: str):
    try:
        message = await ctx.channel.fetch_message(message_id)
        if message.author.id != bot.user.id:
            await ctx.reply("Vous ne pouvez modifier que les messages envoyés par le bot.")
            return
        await message.edit(content=new_content)
        await ctx.reply(f'Message modifié avec succès !')
    except discord.NotFound:
        await ctx.reply(f'Le message avec comme identifiant {message_id} n\'a pas pu être trouvé.')
    except discord.Forbidden:
        await ctx.reply("Vous n'avez pas la permission de modifier ce message.")
    except discord.HTTPException as e:
        await ctx.reply(f"Erreur lors de la modification du message : {e.text}")

@bot.command(help="Débannir un membre")
@commands.has_permissions(manage_messages=True)
async def unban(ctx, user: discord.User):
    try:
        await ctx.guild.unban(user)
        await ctx.reply(f'{user.mention} a été débanni du serveur.')
    except discord.Forbidden:
        await ctx.reply('Je n\'ai pas la permission de débannir les utilisateurs.')
    except discord.HTTPException as e:
        await ctx.reply(f'Erreur : {e.text}')

        
        
print("Démarrage du bot")

bot.run("BOT_TOKEN")
