const baseUrl = window.location.protocol + "//" + window.location.host;
const apiUrl = baseUrl + "/api";

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

function build_websocket(endpoint) {
  const WSocket = new ReconnectingWebSocket(
    "ws://" + window.location.host + "/" + endpoint,
    null,
    {
      debug: true,
      reconnectInterval: randomIntFromInterval(500, 1500),
      maxReconnectInterval: 5000,
      reconnectDecay: 1.1,
    },
  );

  // WSocket.onclose = function (event) {
  //   console.log(event.toString());
  //   console.log("Lost connection to server. Please reload the page.");
  // };
  // WSocket.onerror = function (event) {
  //   console.log(event.toString());
  //   console.log("Error in connection to server. Please reload the page.");
  // };

  return WSocket;
}

function exists(element) {
  return typeof element != "undefined" && element != null;
}

function queryAPI(endpoint, method, data = null) {
  const url = apiUrl + "/" + endpoint;
  const headers = {
    "Content-Type": "application/json",
  };
  const body = data ? JSON.stringify(data) : null;
  return fetch(url, {
    method: method,
    headers: headers,
    body: body,
  }).then((response) => {
    if (!response.ok) {
      throw new Error("HTTP error " + response.status);
    }
    return response.json();
  });
}

function updateResultsPage() {
  queryAPI("refreshActivePollPage", "PUT").then((data) => {
    console.log("updateResultsPage");
    console.log(data);
  });
}
