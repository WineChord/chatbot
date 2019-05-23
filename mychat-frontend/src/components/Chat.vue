<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-6 offset-3">
        <div v-if="!loading && sessionStarted" id="chat-container" class="card">
          <div class="card-body">
            <div class="container chat-body" ref="chatBody">
              <div v-for="message in messages" :key="message.id" class="row chat-section">
                <template v-if="username === message.user.username">
                  <div class="col-sm-7 offset-3">
                    <span class="card-text speech-bubble speech-bubble-user float-right text-white subtle-blue-gradient">
                      {{ message.message }}
                      <!-- <p>Using v-html directive: <span v-html="message.message"></span></p> -->
                    </span>
                  </div>
                  <div class="col-sm-2">
                    <!--<img class="rounded-circle" :src="`http://placehold.it/40/007bff/fff&text=${message.user.username}`" />
                    -->
                    <p style="font-size:12px" align=right>{{ message.user.username }}</p>
                  </div>
                </template>
                <template v-else>
                  <div class="col-sm-2">
                    <!-- <img class="rounded-circle" :src="`http://placehold.it/40/333333/fff&text=${message.user.username}`" />
                    -->
                    <p style="font-size:12px" align=left>{{ message.user.username }}</p>
                  </div>
                  <div class="col-sm-7">
                    <span class="card-text speech-bubble speech-bubble-peer float-left">
                      <!-- {{ message.message }} -->
                      <!-- <p align="left"> -->
                        <span v-html="message.message"></span>
                      <!-- </p> -->
                    </span>
                  </div>
                </template>
              </div>
            </div>
          </div>

          <div class="card-footer text-muted">
            <form @submit.prevent="postMessage">
              <div class="row">
                <div class="col-sm-10">
                  <input v-model="message" type="text" placeholder="Type a message" />
                </div>
                <div class="col-sm-2">
                  <button class="btn btn-primary">Send</button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <div v-else-if="!loading && !sessionStarted">
          <h3 class="text-center">Welcome {{ username }}!</h3>
          <br />
          <p class="text-center">
            To start chatting with friends click on the button below, it'll start a new chat session
            and then you can invite your friends over to chat!
          </p>
          <br />
          <button @click="startChatSession" class="btn btn-primary btn-lg btn-block">Start Chatting</button>
        </div>

        <div v-else>
          <div class="loading">
            <h4>Loading...</h4>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const $ = window.jQuery

export default {
  data () {
    console.log('entering data')
    return {
      loading: true,
      sessionStarted: false,
      // messages: [
      //   { 'status': 'SUCCESS', 'uri': 'ffec00475c7d47c', 'message': 'Hello!', 'user': { 'id': 11, 'username': 'chat11', 'email': '', 'first_name': '', 'last_name': '' } },
      //   { 'status': 'SUCCESS', 'uri': 'ffec00475c7d47c', 'message': 'Hey whatsup! i dey', 'user': { 'id': 12, 'username': 'chat12', 'email': '', 'first_name': '', 'last_name': '' } }
      // ]
      messages: [],
      message: ''
    }
  },

  created () {
    console.log('entering create')
    this.username = sessionStorage.getItem('username')

    // Setup headers for all requests
    $.ajaxSetup({
      headers: {
        'Authorization': `Token ${sessionStorage.getItem('authToken')}`
      }
    })
    // join chat session
    if (this.$route.params.uri) {
      this.joinChatSession()
      console.log('entering joinChatSession')
      // this.connectToWebSocket()
      console.log('connecting to websocket...')
    }
    setTimeout(() => { this.loading = false }, 20)
    setInterval(this.fetchChatSessionHistory, 500)
  },
  updated () {
    // Scroll to bottom of Chat window
    console.log('entering updated...')
    const chatBody = this.$refs.chatBody
    console.log(chatBody)
    if (chatBody) {
      // console.log('chatbody is true')
      chatBody.scrollTop = chatBody.scrollHeight
    }
  },
  methods: {
    startChatSession () {
      $.post('http://localhost:8000/api/chats/', (data) => {
        alert("A new session has been created and you'll be redirected automatically.")
        this.sessionStarted = true
        this.$router.push(`/chats/${data.uri}/`)
      })
        .fail((response) => {
          alert(response.responseText)
        })
      // this.sessionStarted = true
      // this.$router.push('/chats/chat_url/')
    },

    postMessage (event) {
      const data = {message: this.message}
      console.log('entering postMessage...')
      console.log(data)
      $.post(`http://localhost:8000/api/chats/${this.$route.params.uri}/messages/`, data, (data) => {
        // this.messages.push(data)
        // console.log(this.messages)
        this.message = '' // clear the message after sending
      })
        .fail((response) => {
          alert(response.responseText)
        })
    },

    joinChatSession () {
      const uri = this.$route.params.uri

      $.ajax({
        url: `http://localhost:8000/api/chats/${uri}/`,
        data: {username: this.username},
        type: 'PATCH',
        success: (data) => {
          const user = data.members.find((member) => member.username === this.username)
          if (user) {
            // The user belongs/has joined the session
            this.sessionStarted = true
            console.log('entering fetchChatSessionHistory')
            this.fetchChatSessionHistory()
          }
        }
      })
    },

    fetchChatSessionHistory () {
      $.get(`http://localhost:8000/api/chats/${this.$route.params.uri}/messages/`, (data) => {
        console.log(data.messages.length)
        console.log(this.messages.length)
        if (data.messages.length !== this.messages.length) {
          this.messages = data.messages
        }
        console.log(this.messages)
      })
    },

    connectToWebSocket () {
      console.log(this.$route.params.uri)
      const websocket = new WebSocket(`ws://localhost:8081/${this.$route.params.uri}`)
      websocket.onopen = this.onOpen
      websocket.onclose = this.onClose
      websocket.onmessage = this.onMessage
      websocket.onerror = this.onError
    },

    onOpen (event) {
      console.log('Connection opened.', event.data)
    },

    onClose (event) {
      console.log('Connection closed.', event.data)
      // Try and Reconnect after five seconds
      setTimeout(this.connectToWebSocket, 5000)
    },

    onMessage (event) {
      const message = JSON.parse(event.data)
      this.messages.push(message)
    },

    onError (event) {
      alert('An error occurred:', event.data)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1,
h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}

.btn {
  border-radius: 0 !important;
}

.card-footer input[type="text"] {
  background-color: #ffffff;
  color: #444444;
  padding: 7px;
  font-size: 13px;
  border: 2px solid #cccccc;
  width: 100%;
  height: 38px;
}

.card-header a {
  text-decoration: underline;
}

.card-body {
  background-color: #ddd;
}

.chat-body {
  margin-top: -15px;
  margin-bottom: -5px;
  height: 550px;
  overflow-y: auto;
}

.speech-bubble {
  display: inline-block;
  position: relative;
  border-radius: 0.4em;
  padding: 10px;
  background-color: #fff;
  font-size: 14px;
}

.subtle-blue-gradient {
  background: linear-gradient(45deg,#004bff, #007bff);
}

.speech-bubble-user:after {
  content: "";
  position: absolute;
  right: 4px;
  top: 10px;
  width: 0;
  height: 0;
  border: 20px solid transparent;
  border-left-color: #007bff;
  border-right: 0;
  border-top: 0;
  margin-top: -10px;
  margin-right: -20px;
}

.speech-bubble-peer:after {
  content: "";
  position: absolute;
  left: 3px;
  top: 10px;
  width: 0;
  height: 0;
  border: 20px solid transparent;
  border-right-color: #ffffff;
  border-top: 0;
  border-left: 0;
  margin-top: -10px;
  margin-left: -20px;
}

.chat-section:first-child {
  margin-top: 10px;
}

.chat-section {
  margin-top: 15px;
}

.send-section {
  margin-bottom: -20px;
  padding-bottom: 10px;
}
</style>
