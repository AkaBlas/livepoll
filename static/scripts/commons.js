const baseUrl = window.location.protocol + "//" + window.location.host;
const apiUrl = baseUrl + "/api";
const WSocket = new WebSocket("ws://" + window.location.host + "/websocket");

function exists(element) {
  return typeof element != "undefined" && element != null;
}
