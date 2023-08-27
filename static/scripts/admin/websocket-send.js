function makeIdle() {
  console.log("makeIdle");
  var data = {
    active_poll: null,
  };
  sendWSSocket(data);
  updateCheckboxes();
}

function updateActivePoll(poll_uid) {
  console.log("updateActivePoll: " + poll_uid);
  var data = {
    active_poll: poll_uid,
  };
  sendWSSocket(data);
  updateCheckboxes(poll_uid);
}
