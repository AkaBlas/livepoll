// // const baseUrl = window.location.protocol + "//" + window.location.host;
// // const apiUrl = baseUrl + "/api";
// // const WSocket = new WebSocket("ws://" + window.location.host + "/websocketVoting");

const optionOneButton = document.getElementById("option_one");
const optionTwoButton = document.getElementById("option_two");

function sendVote(poll_uid) {
  pollCookie.addVote(poll_uid, getSelectedOption());
  document.getElementById("thanks").style.visibility = "inherit";
}

function getSelectedOption() {
  if (optionOneButton.checked) {
    return optionOneButton.value;
  }
  return optionTwoButton.value;
}
