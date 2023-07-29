from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from pprint import PrettyPrinter
from os import scandir, mkdir
from json import dump, load
from Modules.config import TOKEN
from Modules.messages import MESSAGES

vk_session = VkApi(token=TOKEN)
longpool = VkBotLongPoll(vk_session, group_id=221700248)

def send_some_msg(id, some_text):
	vk_session.method("messages.send", {"chat_id":id, "message":some_text,"random_id":0})

def to_int(s):
	try:
		s = int(s)
	except TypeError:
		s = None
	return s

for event in longpool.listen():
	if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
		msg = event.message.get('text').lower()
		members_info = vk_session.method("messages.getConversationMembers", {"peer_id": event.object.message['peer_id']})
		id = event.chat_id

		list_cmds = [' help', ' info', ' top']

		list_chats = [to_int(file.name) for file in scandir("Data/Chats") if file.is_dir()]

		list_minus = ['rep-']
		list_plus = ['rep+']

		# Добавление уже созданых ассоциаций
		if id in list_chats:
			with open(f"Data/Chats/{id}/associations.json", 'r') as file:
				associations = load(file)
				list_minus += associations['-']
				list_plus += associations['+']

		if msg.startswith('rep') or msg in list_minus+list_plus:

			if msg[3:] == ' start':

				if id not in list_chats:
					members_rep = {
						str(item['member_id']):{'reputation':0,'last_plus':{}} 
						for item in members_info['items'] if 0 < item['member_id']
					}
					associations = {
						'+' : [],
						'-' : []
					}
					mkdir(f"Data/Chats/{id}")
					with open(f"Data/Chats/{id}/users.json", 'w') as File:
						dump(members_rep, File, indent=4)
					with open(f"Data/Chats/{id}/associations.json", 'w') as File:
						dump(associations, File, indent=4)
					send_some_msg(id, MESSAGES['start'])
				else:
					send_some_msg(id, MESSAGES['not-start'])

			elif msg[3:] in list_cmds or msg in list_minus+list_plus:

				reaply_msg = event.message.reply_message

				if reaply_msg != None:
					info_reaply = [profile for profile in members_info['profiles'] if profile['id'] == reaply_msg['from_id']][0]

				if id not in list_chats:
					send_some_msg(id, MESSAGES['not-registr'])

				elif msg in list_minus+list_plus and reaply_msg != None and reaply_msg['from_id'] > 0:
					# "rep+"

					with open(f"Data/Chats/{id}/users.json", 'r') as File:
						members_rep = load(File)

					coulddown = event.message['date'] - members_rep[str(event.message['from_id'])]['last_plus'].get(str(reaply_msg['from_id']),0)

					if reaply_msg['from_id'] == event.message['from_id']:
						send_some_msg(id, MESSAGES['self'])

					elif coulddown <= 7200:
						send_some_msg(id, MESSAGES['rep-coulddown'].format(119 - coulddown // 60))

					else:
						
						if msg in list_plus:
							members_rep[str(reaply_msg['from_id'])]['reputation'] += 1
							send_some_msg(id, MESSAGES['plus-rep'].format(info_reaply['id'],info_reaply['first_name']))
						else:
							members_rep[str(reaply_msg['from_id'])]['reputation'] -= 1
							send_some_msg(id, MESSAGES['minus-rep'].format(info_reaply['id'],info_reaply['first_name']))

						members_rep[str(event.message['from_id'])]['last_plus'][str(reaply_msg['from_id'])] = event.message['date']

						with open(f"Data/Chats/{id}/users.json", 'w') as File:
							dump(members_rep, File, indent=4)

				elif msg[3:] == list_cmds[2]:
					# "rep help"
					pass

				elif msg[3:] == list_cmds[3] and reaply_msg != None and reaply_msg['from_id'] > 0:

					with open(f"Data/Chats/{id}/users.json", 'r') as File:
						send_some_msg(id, MESSAGES['info'].format(info_reaply['id'],info_reaply['first_name'],load(File)[str(reaply_msg['from_id'])]['reputation']))
	

		if msg in ['чмонус']:
			send_some_msg(id, f'Вы чмонус!')

		pp = PrettyPrinter(indent=4)
		pp.pprint(event.message)

		# pprint(vk_session.method("messages.getConversationMembers", {"peer_id": event.object.message['peer_id']}))
		# print(event.object.message['peer_id'])

		# quit()