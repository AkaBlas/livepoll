let cookie_name = "poll_votes";

function setCookie(value, name = cookie_name, expire_days = 365) {
  const d = new Date();
  d.setTime(d.getTime() + expire_days * 24 * 60 * 60 * 1000);
  let expires = "expires=" + d.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function getCookie(name = cookie_name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function getCookiePollVotes() {
  let cookie = getCookie();
  if (cookie === "" || cookie === undefined) {
    return {};
  }
  return JSON.parse(cookie);
}

function setCookiePollVotes(votes) {
  setCookie(JSON.stringify(votes));
}

class PollCookie {
  constructor() {
    this.votes = getCookiePollVotes();
  }

  addVote(poll_uid, option_uid, previous_option_uid = null) {
    if (previous_option_uid === null && this.votes.hasOwnProperty(poll_uid)) {
      previous_option_uid = this.votes[poll_uid].option_uid;
    }

    console.log(
      "Adding vote: " + poll_uid + " " + option_uid + " " + previous_option_uid,
    );

    if (!this.votes.hasOwnProperty(poll_uid)) {
      this.votes[poll_uid] = {};
      this.votes[poll_uid].poll_uid = poll_uid;
    }
    this.votes[poll_uid].option_uid = option_uid;
    this.votes[poll_uid].previous_option_uid = previous_option_uid;
    setCookiePollVotes(this.votes);
    WSocket.send(
      JSON.stringify({
        add_poll_vote: {
          poll_uid: poll_uid,
          option_uid: option_uid,
          previous_option_uid: previous_option_uid,
        },
      }),
    );
  }

  getVote(poll_uid) {
    if (!this.hasVote(poll_uid)) {
      return null;
    }
    console.log("Getting vote: " + poll_uid);
    console.log("Current Vote is: " + this.votes[poll_uid]);
    return this.votes[poll_uid];
  }

  hasVote(poll_uid) {
    return this.votes.hasOwnProperty(poll_uid);
  }

  getCurrentOptionID(poll_uid) {
    if (!this.getVote(poll_uid)) {
      return "";
    }
    return this.getVote(poll_uid).option_uid;
  }
}

let pollCookie = new PollCookie();
