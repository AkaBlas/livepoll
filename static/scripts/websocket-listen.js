WSocket.onclose = function (event) {
  console.log(event.toString());
  alert("Lost connection to server. Please reload the page.");
};
WSocket.onerror = function (event) {
  console.log(event.toString());
  alert("Error in connection to server. Please reload the page.");
};

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

    document.getElementById("active-poll-question").innerHTML =
      jsonData.active_poll.question;
    document.getElementById("option_one").value =
      jsonData.active_poll.option_one.uid;
    document.getElementById("option_two").value =
      jsonData.active_poll.option_two.uid;
    document.getElementById("option_one_label").innerHTML =
      jsonData.active_poll.option_one.text +
      ", Stimmen: " +
      jsonData.active_poll.option_one.votes;
    document.getElementById("option_two_label").innerHTML =
      jsonData.active_poll.option_two.text +
      ", Stimmen: " +
      jsonData.active_poll.option_two.votes;
    document.getElementById("option_one").onchange = function () {
      sendVote(jsonData.active_poll.uid);
    };
    document.getElementById("option_two").onchange = function () {
      sendVote(jsonData.active_poll.uid);
    };
    document.getElementById("option_one").checked =
      pollCookie.getCurrentOptionID(jsonData.active_poll.uid) ===
      jsonData.active_poll.option_one.uid;
    document.getElementById("option_two").checked =
      pollCookie.getCurrentOptionID(jsonData.active_poll.uid) ===
      jsonData.active_poll.option_two.uid;
  }
};
