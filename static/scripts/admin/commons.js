const WSocket = build_websocket("websocketAdmin");

function sendWSSocket(data) {
  WSocket.send(JSON.stringify(data));
}

function updateCheckboxes(poll_uid = null) {
  console.log("updateCheckboxes: " + poll_uid);
  const checkboxes = document.querySelectorAll('[id^="update-poll-"]');
  checkboxes.forEach((checkbox) => {
    if (poll_uid === null) {
      checkbox.checked = false;
      return;
    }
    checkbox.checked = checkbox.id === "update-poll-" + poll_uid;
  });
}
