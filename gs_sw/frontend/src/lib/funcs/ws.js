// src/lib/funcs/ws.js
import ReconnectingWebSocket from "reconnecting-websocket";

let WS_URL = "ws://localhost:5556";

const ws = new ReconnectingWebSocket(WS_URL);

let wsConnected = false;

// track connection state (and swallow errors so they don't bubble)
ws.addEventListener("open", () => (wsConnected = true));
ws.addEventListener("close", () => (wsConnected = false));
ws.addEventListener("error", () => (wsConnected = false));

// tiny helper: only send if open; otherwise no-op
function sendIfOpen(ws, data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(data);
  };
}

export function sendCmd(cmd_name) {
  const packed = {
    "cmd" : cmd_name
  };
  const jsonString = JSON.stringify(packed);
  console.log(jsonString)
  sendIfOpen(ws, jsonString);
}

export function sendRC(x,y,z,r) {
  const packed = {
    "rc" : [x,y,z,r]
  };
  const jsonString = JSON.stringify(packed);
  sendIfOpen(ws, jsonString);
}

// optional: expose status if your UI wants to gray out controls
export function wsStatus() {
  return wsConnected;
}
