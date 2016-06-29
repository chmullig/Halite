function getGET(name) {
	name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
	results = regex.exec(location.search);
	return results === null ? null : decodeURIComponent(results[1].replace(/\+/g, " "));
}

$(function() {
	function SmartForm($submitButton, $form, onSubmit) {
		$submitButton.click(function() {
			console.log("CLICK");
			onSubmit();
		});
		$form.keypress(function(event) {
			if (event.which == 13) {
				event.preventDefault();
				onSubmit();
			}
		});
	};

	var navbar = {
		loggedIn: false,
		$logInUsername: $("#login_user"),
		$logInPassword: $("#login_pass"),
		$logInButton: $("#loginButton"),
		$logInForm: $("#loginForm"),
		$registerUsername: $("#register_user"),
		$registerEmail: $("#register_email"),
		$registerPassword: $("#register_pass"),
		$registerButton: $("#registerButton"),
		$registerForm: $("#registerForm"),
		$logInNav: $("#loginNav"),
		$logOutNav: $("#logoutNav"),
		$logOutButton: $("#logoutButton"),

		uploadButton: {
			$button: $("#submitButton"),
			$form: $("#submitForm"),
			$fileInput: $("#myFile"),
			init: function() {
				this.$button.click(this, this.buttonClicked.bind(this));
				this.$fileInput.change(this, this.fileChanged.bind(this));
			},
			setUserID: function(userID) {
				this.$form.append("<input type='hidden' name='userID' value='"+userID+"'>");
			},
			buttonClicked: function() { this.$fileInput.click(); },
			fileChanged: function() {
				storeBotFile("submitForm");
				messageBox.alert("Bot Submitted", "Your bot was successfully uploaded to our servers. You should show up on the leaderboard within a couple of minutes.", true)
			}
		},

		init: function() {
			new SmartForm(this.$logInButton, this.$logInForm, this.logIn.bind(this));
			new SmartForm(this.$registerButton, this.$registerForm, this.register.bind(this));

			this.uploadButton.init();
			this.$logOutButton.click(this.logOut.bind(this));

			var session = getSession();
			if(session != null && session.userID != null) {
				this.user = session;
				this.loggedIn = true;
			}

			this.render();
		},
		logIn: function() {
			var user = getUser(null, this.$logInUsername.val(), this.$logInPassword.val());
			if(user == null) {
				messageBox.alert("Login failed", "That username/password combo does not exist", false);
			} else {
				storeUserSession(this.$logInUsername.val(), this.$logInPassword.val(), false);
				this.loggedIn = true;
				this.user = user;
				this.render();
			}
		},
		register: function() {
			var username = this.$registerUsername.val();
			var email = this.$registerEmail.val();
			var password = this.$registerPassword.val();

			var resp = storeUserDatabase(email, username, password, false);
			if (resp === "Success") {
				storeUserSession(username, password, false);

				this.loggedIn = true;
				this.user = getSession();
				this.render();
				messageBox.alert("Registration succeeded", "You successfully registered and were logged in for the Halite competition.", true);
			} else  {
				if(resp.toLowerCase().indexOf("usernmae") > -1) {
					messageBox.alert("Registration failed", "That username is already taken", false);
				} else {
					messageBox.alert("Registration failed", "That email is already taken", false);
				}
			}
		},
		logOut: function() {
			destroySession(false);
			this.loggedIn = false;
			this.render();
		},
		render: function() {
			if(this.loggedIn) {
				this.$logInNav.css("display", "none");
				this.$logOutNav.css("display", "inline");

				this.uploadButton.setUserID(this.user.userID);
			} else {
				this.$logInNav.css("display", "inline");
				this.$logOutNav.css("display", "none");
			}
		}
	}

	navbar.init();
})
