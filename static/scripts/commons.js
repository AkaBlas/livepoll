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
