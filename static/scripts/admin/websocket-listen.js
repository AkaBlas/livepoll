function updateActivePollData(poll) {
  document.getElementById("active-poll-question").innerHTML = poll.question;
  document.getElementById("option-one-text").innerHTML = poll.option_one.text;
  document.getElementById("option-two-text").innerHTML = poll.option_two.text;
  document.getElementById("option-one-votes").innerHTML = poll.option_one.votes;
  document.getElementById("option-two-votes").innerHTML = poll.option_two.votes;
}

WSocket.onmessage = function (event) {
  const jsonData = JSON.parse(event.data);
  if (jsonData.idle !== undefined) {
    console.log("idle: " + jsonData.idle);
    document.getElementById("active-poll").style.display = "none";
    document.getElementById("idle").style.display = "block";
    updateCheckboxes();
    return;
  }
  if (jsonData.active_poll !== undefined) {
    console.log("active_poll: " + jsonData.active_poll);
    document.getElementById("idle").style.display = "none";
    document.getElementById("active-poll").style.display = "block";
    updateActivePollData(jsonData.active_poll);
    updateCheckboxes(jsonData.active_poll.uid);
    return;
  }
  if (jsonData.poll_update !== undefined) {
    console.log("poll_update: " + jsonData.poll_update);
    document.getElementById(
      "votes-option-one-" + jsonData.poll_update.option_one.uid,
    ).innerHTML = jsonData.poll_update.option_one.votes;
    document.getElementById(
      "votes-option-two-" + jsonData.poll_update.option_two.uid,
    ).innerHTML = jsonData.poll_update.option_two.votes;
    updateActivePollData(jsonData.poll_update);
    return;
  }
  console.log("Unknown message: " + event.data);
};
