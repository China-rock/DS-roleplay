import os
import gradio as gr
from openai import OpenAI

api_key = os.environ.get("MY_API_KEY")

client =OpenAI(api_key=api_key,
base_url="https://api.deepseek.com")

default_prompt =" "

def chat_function(message, history,system_prompt):

	print(f"收到请求，正在调用API")

	messages=[{"role":"system","content": system_prompt}]
	for msg in history:
		content=msg["content"]
		if isinstance(content,list):
			content="".join([c["text"]for c in content if"text"in c])
		messages.append({"role":msg["role"],"content":content})
	if isinstance(message,list):
		message="".join([c["text"]for c in message if"text"in c])
	messages.append({"role":"user","content":message})
	
	try:
		response =client.chat.completions.create(
			model="deepseek-chat",
			messages=messages
		)
		print("\n===后台返回了:===")
		print(response)
		print("=================\n")
		return response.choices[0].message.content

	except Exception as e:
		print(f"\n===报错了:{e}===\n")
		return f"哎呀，出错了: {e}"

with gr.Blocks(theme="glass",title="给你们的小玩具，可以角色扮演，人设自由输入") as demo:
	gr.Markdown("#角色扮演")
	gr.Markdown("在这里，你可以和你想要的角色对话，只要输入ta的人设即可")

	prompt_box = gr.Textbox(
		value="",
		label="在这里输入人设(随意改)不填就是默认deep seek",
		placeholder="你可以在这里输入任何设定",
		lines=4
	)
	chatbot = gr.Chatbot(height=400)
	
	msg = gr.Textbox(label="输入你想说的话，按回车发送，动作可以写在括号里")
	clear = gr.Button("清空对话")

	def user(user_message,history):
		return " ", history +[{"role":"user","content":user_message}]
	def bot(history, system_prompt):
		user_message = history[-1]["content"]
		if isinstance(user_message,list):
			user_message="".join([c["text"]for c in user_message if"text"in c])

		bot_message =chat_function(user_message , history[:-1],system_prompt)

		if bot_message is None:
			bot_message="(网络开小差了，请重试)"

		history.append({"role":"assistant","content":bot_message})
		return history

	msg.submit(user, [msg, chatbot], [msg,chatbot], queue=False).then(
		bot, [chatbot, prompt_box],chatbot
	)
	clear.click(lambda:None, None,chatbot, queue=False)

if __name__=="__main__":
	demo.launch()
		
