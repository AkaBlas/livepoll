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

    const total_votes = Math.max(
      1,
      jsonData.active_poll.option_one.votes +
        jsonData.active_poll.option_two.votes,
    );
    const option_one_percentage =
      (100 * jsonData.active_poll.option_one.votes) / total_votes;
    const option_two_percentage =
      (100 * jsonData.active_poll.option_two.votes) / total_votes;

    document.getElementById("option-one-bar").style.width =
      option_one_percentage + "%";
    document.getElementById("option-two-bar").style.width =
      option_two_percentage + "%";

    text_animation(
      document.getElementById("option-one-percentage"),
      option_one_percentage.toFixed(1),
      1.25,
    );
    text_animation(
      document.getElementById("option-two-percentage"),
      option_two_percentage.toFixed(1),
      1.25,
    );
  }

  function text_animation(element, target, duration) {
    const fps = 30;
    const frames = Math.ceil(fps * duration);
    console.log("frames: " + frames);
    const float_target = parseFloat(target);
    const element_content = parseFloat(element.innerHTML.replace(" %", ""));

    console.log("element_content: " + element_content);
    console.log(
      "target - element_content: " + (float_target - element_content),
    );

    const increment = (float_target - element_content) / frames;
    console.log("increment: " + increment);

    let frame = 0;
    const interval = setInterval(function () {
      // console.log("frame: " + frame, "element_content: " + element_content, "increment: " + increment);
      element.innerHTML = format_percentage(
        element_content + frame * increment,
      );
      frame++;
      if (frame >= frames) {
        clearInterval(interval);
        element.innerHTML = format_percentage(float_target);
        return;
      }
    }, 1000 / fps);
  }

  function format_percentage(percentage) {
    return percentage.toFixed(1) + " %";
  }
};
