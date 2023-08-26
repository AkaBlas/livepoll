function refreshActivePoll() {
  fetch(apiUrl + "/activePoll", {
    headers: { "Content-Type": "application/json" },
    method: "GET",
  })
    .then((response) => {
      if (response.status === 404) {
        return null;
      }
      if (response.ok) {
        return response.json();
      } else {
        console.log("Could not get active Poll: " + response.statusText);
      }
    })
    .then((json) => {
      if (json === null) {
        document.getElementById("active-poll").style.display = "none";
        document.getElementById("idle").style.display = "block";
      } else {
        document.getElementById("idle").style.display = "none";
        document.getElementById("active-poll").style.display = "block";

        document.getElementById("active-poll-question").innerHTML =
          json.question;
        document.getElementById("option-one-text").innerHTML =
          json.option_one.text;
        document.getElementById("option-two-text").innerHTML =
          json.option_two.text;
        document.getElementById("option-one-votes").innerHTML =
          json.option_one.votes;
        document.getElementById("option-two-votes").innerHTML =
          json.option_two.votes;
      }
    });
}
