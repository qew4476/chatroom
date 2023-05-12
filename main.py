from typing import List
from fastapi import FastAPI
from starlette.endpoints import WebSocketEndpoint, HTTPEndpoint
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from userID import info

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
<style>
body
{
	background-color:#b0c4de;
}
</style>
    </head>
    <body>
        <h1 style="text-align: center;">Chatroom</h1>
        <form style="position:absolute; right:40%;"action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" placeholder="" />
            <button style="	background-color:#44c767;
	border-radius:28px;
	border:1px solid #18ab29;
	display:inline-block;
	cursor:pointer;
	color:#ffffff;
	font-family:Arial;
	font-size:17px;
	padding:16px 31px;
	text-decoration:none;
	text-shadow:0px 1px 0px #2f6627;">Send</button>
        </form>
        <ul style="position:absolute; right:50%; Top:20% " id='messages'>
        </ul>
        <script>
            document.getElementById("messageText").placeholder="Please input your ID";
        
            var ws = new WebSocket("ws://localhost:8000/ws");
            
            
            ws.onmessage = function(event) {
                
                var messages = document.getElementById('messages')
                
                var message = document.createElement('li')
                
                var content = document.createTextNode(event.data)
                
                message.appendChild(content)
                
                messages.appendChild(message)
            };
            
            var name = 0;
            
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
                
                if (name == 0){
                    document.getElementById("messageText").placeholder="";
                    name = 1;
                }
            }
        </script>
    </body>
</html>
"""


class Homepage(HTTPEndpoint):
    async def get(self, request):
        return HTMLResponse(html)


class Echo(WebSocketEndpoint):
    encoding = "text"

    # edit socket
    async def alter_socket(self, websocket):
        socket_str = str(websocket)[1:-1]
        socket_list = socket_str.split(" ")
        socket_only = socket_list[3]
        return socket_only

    # connect
    async def on_connect(self, websocket):
        await websocket.accept()

        # input client ID
        name = await websocket.receive_text()

        socket_only = await self.alter_socket(websocket)
        # save ID and socket
        info[socket_only] = [f"{name}", websocket]

        # Tell everyone that someone has joined
        for wbs in info:
            await info[wbs][1].send_text(f"{info[socket_only][0]} joined the chatroom")

        print(info)

    # receive
    async def on_receive(self, websocket, data):
        socket_only = await self.alter_socket(websocket)

        for wbs in info:
            await info[wbs][1].send_text(f"{info[socket_only][0]}: {data}")

    # disconnect
    async def on_disconnect(self, websocket, close_code):
        socket_only = await self.alter_socket(websocket)
        info.pop(socket_only)
        print(info)
        pass


routes = [Route("/", Homepage), WebSocketRoute("/ws", Echo)]

app = FastAPI(routes=routes)
