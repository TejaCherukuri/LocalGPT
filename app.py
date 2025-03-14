import chainlit as cl
import ollama
import time

@cl.on_chat_start
async def start():
    cl.user_session.set(
        "interaction",
        [
            {
                "role": "system",
                "content": "You are a helpful AI assistant.",
            }
        ],
    )

    message = cl.Message(content="")
    start_message = "Hello, I'm your LocalGPT. How can I help you today?"

    for token in start_message:
        await message.stream_token(token)
        time.sleep(0.005)

    await message.send()

@cl.step(type="tool")
async def tool(input_message, image=None):

    interaction = cl.user_session.get("interaction")

    if image:
        interaction.append({"role": "user",
                            "content": input_message,
                            "images": image})
    else:
        interaction.append({"role": "user",
                            "content": input_message})
    
    response = ollama.chat(model="gemma3:1b",
                           messages=interaction) 
    
    interaction.append({"role": "assistant",
                        "content": response.message.content})
    
    return response


@cl.on_message 
async def main(msg: cl.Message):

    images = [file for file in msg.elements if "image" in file.mime]

    if images:
        response = await tool(msg.content, [i.path for i in images])
    else:
        response = await tool(msg.content)

    message = cl.Message(content="")

    for token in response.message.content:
        await message.stream_token(token)

    await message.send()