$(function() {
	var gameDisplay = {
		isInitialized: false,
		init: function() {
			this.isInitialized = true;
			this.cacheDOM();
		},
		cacheDOM: function() {
			this.$modal = $("#gameModal");
			this.$player1Field = $("#player1");
			this.$player2Field = $("#player2");
		},
		setGame: function(player1Name, player2Name, replayContents) {
			if(this.isInitialized == false) this.init();

			this.player1Name = player1Name;
			this.player2Name = player2Name;
			this.replayContents = replayContents;
			this.render();
		},
		render: function() {
			this.$modal.modal('show');
			this.$player1Field.html(this.player1Name);
			this.$player2Field.html(this.player2Name);
			begin(this.replayContents);
		},
		hide: function() {
			this.$modal.modal('hide');
		}
	};

	var messageBox = {
		$messageBox: $("#messageBox"),
		alert: function(title, message, isSuccess) {
			this.$messageBox.empty()
			this.$messageBox.append($("<div class='alert "+(isSuccess ? "alert-success" : "alert-danger")+" alert-dismissible' role='alert'><button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button><strong>"+title+"</strong>&nbsp;&nbsp;"+message+"</div>"))
		}
	};

	function GameDropdown(user, $parentField) {
		this.setGames = function(games) {
			console.log(games)
			this.games = games;
			this.render();
			this.hide();
		};
		this.render = function() {
			this.$parentField.find(".gameRow").remove();
			for(var a = 0; a < this.games.length; a++) {
				var opponent = this.games[a].users[0].userID == this.user.userID ? this.games[a].users[1] : this.games[a].users[0];
				var gameResult = opponent.rank === "0" ? "Lost" : "Won";

				this.$parentField.append("<tr class='gameRow'><td></td><td>vs "+opponent.username+"</td><td>"+opponent.language+"</td><td><span class='"+gameResult.toLowerCase()+"'>"+gameResult+"</span></td><td><a gameID='"+this.games[a].gameID+"' class='gameLink"+this.user.userID+"' target='_blank' href='../storage/replays/"+this.games[a].replayName+"'><img class='file-icon' src='assets/file.png'></a></td></tr>");
			}
		};
		this.toggle = function() {
			if(this.isShown == true) this.hide();
			else this.show();
		};
		this.hide = function() {
			this.isShown = false;
			this.$parentField.find(".arrow").attr('src', "assets/up-arrow.png");
			this.$parentField.find(".gameRow").css("display", "none");
		};
		this.show = function() {
			this.isShown = true;
			this.$parentField.find(".arrow").attr('src', "assets/down-arrow.png");
			this.$parentField.find(".gameRow").css("display", "table-row");
		};
		/*this.displayGame = function(event) {
			var gameID = $(event.target).attr("gameID");
			var game = null;
			for(var a = 0; a < this.games.length; a++) if (this.games[a].gameID == gameID) game = this.games[a];

			var users = game.users;
			users.sort(function(a, b) {
				return a.playerIndex > b.playerIndex;
			});

			gameDisplay.setGame(users[0].username, users[1].username, getGameFile(game.replayName));
		};*/

		this.user = user;
		this.$parentField = $parentField;
		//$(document).on("click", ".gameLink"+this.user.userID, this.downloadGame.bind(this));
	};

	var table = {
		init: function(submissions) {
			this.cacheDOM();
			this.bindEvents();
			this.setSubmissions(submissions);
		},
		cacheDOM: function() {
			this.$table = $("#leaderTable")
		},
		bindEvents: function() {
			$(document).on("click", ".matchDrop", this.toggleDropdown.bind(this));
		},
		setSubmissions: function(submissions) {
			this.submissions = submissions;

			this.render();

			this.dropdowns = Array();
			for(var a = 0; a < this.submissions.length; a++) this.dropdowns.push(new GameDropdown(this.submissions[a], $("#user"+this.submissions[a].userID)));
		},
		render: function() {
			this.$table.find("tbody").remove();
			this.submissions.sort(function(a, b) {
				return a.mu-(a.sigma*3) < b.mu-(b.sigma*3);
			});
			console.log(this.submissions)
			for(var a = 0; a < this.submissions.length; a++) {
				var user = this.submissions[a];
				var score = Math.round((this.submissions[a].mu-(3*this.submissions[a].sigma))*100)/100;
				this.$table.append("<tbody id='user" + user.userID + "'><tr><th scope='row'>"+(a+1)+"</th><td><a href='user.php?userID="+user.userID+"'>"+user.username+"</a></td><td>"+user.language+"</td><td>"+score+"</td><td><img class='matchDrop arrow' userID='"+user.userID+"' src='assets/up-arrow.png'></td></tr></tbody>");
			}
		},
		toggleDropdown: function(event) {
			var user = this.getUserWithID($(event.target).attr("userID"));
			for(var a = 0; a < this.submissions.length; a++) {
				if(this.submissions[a].userID == user.userID) {
					console.log(user.userID)
					if(this.dropdowns[a].games == null) this.dropdowns[a].setGames(getLatestGamesForUser(user.userID));
					this.dropdowns[a].toggle();
					break;
				}
			}
		},
		getUserWithID: function(userID) {
			for(var a = 0; a < this.submissions.length; a++) if(this.submissions[a].userID == userID) return this.submissions[a];
			return getUser(userID);
		}
	};

	table.init(getActiveUsers());
})
