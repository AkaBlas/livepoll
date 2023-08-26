const WSocket = build_websocket("websocketResults");

WSocket.onmessage = function (event) {
  const jsonData = JSON.parse(event.data);
  if (jsonData.idle !== undefined) {
    console.log("idle: " + jsonData.idle);
    document.getElementById("active-poll").style.display = "none";
    document.getElementById("idle").style.display = "block";
    return;
  }
  if (jsonData.active_poll !== undefined) {
    console.log("active_poll: " + jsonData.active_poll);
    document.getElementById("idle").style.display = "none";
    document.getElementById("active-poll").style.display = "block";

    document.getElementById("idle").style.display = "none";
    document.getElementById("active-poll").style.display = "block";

    document.getElementById("active-poll-question").innerHTML =
      jsonData.active_poll.question;
    document.getElementById("option-one-text").innerHTML =
      jsonData.active_poll.option_one.text;
    document.getElementById("option-two-text").innerHTML =
      jsonData.active_poll.option_two.text;
    document.getElementById("option-one-votes").innerHTML =
      jsonData.active_poll.option_one.votes;
    document.getElementById("option-two-votes").innerHTML =
      jsonData.active_poll.option_two.votes;
  }
};
