const baseUrl = window.location.protocol + "//" + window.location.host;
const apiUrl = baseUrl + "/api";

function build_websocket(endpoint) {
  const WSocket = new WebSocket(
    "ws://" + window.location.host + "/" + endpoint,
  );

  WSocket.onclose = function (event) {
    console.log(event.toString());
    alert("Lost connection to server. Please reload the page.");
  };
  WSocket.onerror = function (event) {
    console.log(event.toString());
    alert("Error in connection to server. Please reload the page.");
  };

  return WSocket;
}

function exists(element) {
  return typeof element != "undefined" && element != null;
}
