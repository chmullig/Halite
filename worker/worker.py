import os
import os.path
import stat
import platform
import tempfile
import urllib.request
import requests
import zipfile
import json
from time import sleep
from hashlib import md5
from compiler import *
import trueskill
import configparser
from sandbox import *

RUN_GAME_FILE_NAME = "runGame.sh"

class TrueSkillPlayer(object):
  pass

# Interface between worker and manager RESTFul API
class Backend:
	def __init__(self, apiKey):
		config = configparser.ConfigParser()
		config.read("../halite.ini")
		self.apiKey = apiKey
		self.url = config.get("worker", "managerURL")

        # Gets either a run or a compile task from the API
	def getTask(self):
		print("url: " +self.url+"task")
		content = requests.get(self.url+"task", params={"apiKey": self.apiKey}).text
		print("contents: " + content)
		if content == "null":
			return None
		else:
			return json.loads(content)

	# Allows us to get the hash of a bot's zip file from the server so that we may verify that a bot was downloaded properly
	def getBotHash(self, userID):
		result = requests.get(self.url+"botHash", params={"apiKey": self.apiKey, "userID": userID})
		print("Got bot hash: %s" % (result.text))
		return json.loads(result.text).get("hash")

	# Downloads and store's a bot's zip file locally
	# Checks the file's checksum to make sure the file was downloaded properly
	def storeBotLocally(self, userID, storageDir):
		iterations = 0
		while iterations < 100:
			remoteZip = urllib.request.urlopen(self.url+"botFile?apiKey="+str(self.apiKey)+"&userID="+str(userID))
			zipFilename = remoteZip.headers.get('Content-disposition').split("filename")[1]
			zipPath = os.path.join(storageDir, zipFilename)
			if os.path.exists(zipPath):
				os.remove(zipPath)

			remoteZipContents = remoteZip.read()
			remoteZip.close()

			localZip = open(zipPath, "wb")
			localZip.write(remoteZipContents)
			localZip.close()

			if md5(remoteZipContents).hexdigest() != self.getBotHash(userID):
				iterations += 1
				continue

			return zipPath

		raise ValueError

	# Posts a bot file to the manager
	def storeBotRemotely(self, userID, zipFilePath):
		zipContents = open(zipFilePath, "rb").read()
		iterations = 0

		while iterations < 100:
			r = requests.post(self.url+"botFile", data={"apiKey": self.apiKey, "userID": str(userID)}, files={"bot.zip": zipContents})
			print(r.text)

			# Try again if local and remote hashes differ
			if md5(zipContents).hexdigest() != self.getBotHash(userID):
				print(md5(zipContents).hexdigest())
				print(self.getBotHash(userID))
				print("Hashes do not match!")
				iterations += 1
				continue

			return
		raise ValueError

	# Posts the result of a compilation task
	def compileResult(self, userID, didCompile, language):
		r = requests.post(self.url+"compile", data={"apiKey": self.apiKey, "userID": userID, "didCompile": int(didCompile), "language": language})
		print(r.text)

	# Posts the result of a game task
	def gameResult(self, users, replayPath):
		r = requests.post(self.url+"game", data={"apiKey": self.apiKey, "users": json.dumps(users)}, files={os.path.basename(replayPath): open(replayPath, "rb").read()})
		print(r.text)

# Deletes anything residing at path, creates path, and chmods the directory
def makePath(path):
	if os.path.exists(path):
		shutil.rmtree(path)
	os.makedirs(path)
	os.chmod(path, 0o777)

# Unpacks and deletes a zip file into the files current path
def unpack(filePath):
	folderPath = os.path.dirname(filePath)
	tempPath = os.path.join(folderPath, "bot")
	os.mkdir(tempPath)

	# Extract the archive into a folder call 'bot'
	if platform.system() == 'Windows':
		os.system("7z x -o"+tempPath+" -y "+filePath+". > NUL")
	else:
		os.system("unzip -u -d"+tempPath+" "+filePath+" > /dev/null 2> /dev/null")

	# Remove __MACOSX folder if present
	macFolderPath = os.path.join(tempPath, "__MACOSX")
	if os.path.exists(macFolderPath) and os.path.isdir(macFolderPath):
		shutil.rmtree(macFolderPath)

	# Copy contents of bot folder to folderPath remove bot folder
	for filename in os.listdir(tempPath):
		shutil.move(os.path.join(tempPath, filename), os.path.join(folderPath, filename))

	shutil.rmtree(tempPath)
	os.remove(filePath)

# Zips a folder to a path
def zipFolder(folderPath, destinationFilePath):
	zipFile = zipfile.ZipFile(destinationFilePath, "w", zipfile.ZIP_DEFLATED)

	originalDir = os.getcwd()
	os.chdir(folderPath)

	for rootPath, dirs, files in os.walk("."):
		for file in files:
			if os.path.basename(file) != os.path.basename(destinationFilePath):
				zipFile.write(os.path.join(rootPath, file))

	zipFile.close()

	os.chdir(originalDir)

# Downloads and compiles a bot. Posts the compiled bot files to the manager.
def compile(userID, backend):
	print("Compiling a bot with userID %d" % (userID))

	workingPath = "workingPath"
	makePath(workingPath)
	botPath = backend.storeBotLocally(userID, workingPath)
	unpack(botPath)

	language, errors = compile_anything(workingPath)
	didCompile = True if errors == None else False

	if didCompile:
		print("Bot did compile")
		zipFolder(workingPath, os.path.join(workingPath, str(userID)+".zip"))
		backend.storeBotRemotely(userID, os.path.join(workingPath, str(userID)+".zip"))
	else:
		print("Bot did not compile")
		print(str(errors))

	backend.compileResult(userID, didCompile, language)
	shutil.rmtree(workingPath)

# Downloads compiled bots, runs a game, and posts the results of the game
def runGame(width, height, users, backend):
	print("Running game with width %d, height %d, and users %s" % (width, height, str(users)))

	# Download players to current directory
	for user in users:
		userDir = str(user["userID"])
		if os.path.isdir(userDir):
			shutil.rmtree(userDir)
		os.mkdir(userDir)
		unpack(backend.storeBotLocally(user["userID"], userDir))

	# Run game within sandbox
	runGameCommand = " ".join(["./"+RUN_GAME_FILE_NAME, str(width), str(height), users[0]["userID"], users[1]["userID"]])
	print(runGameCommand)
	sandbox = Sandbox("./")
	sandbox.start("sh -c '/var/www/html/worker/runGame.sh 10 10 31 32'")
    #sandbox.start(runGameCommand)
	lines = []
	while True:
		line = sandbox.read_line(200)
		if line == None:
			break
		print(line)
		lines.append(line)

	replayPath = lines[(len(lines)-len(users)) - 1][len("Failed to output to file. Opening a file at ") :]

	# Get player ranks and scores by parsing shellOutput
	for lineIndex in range(len(lines) - len(users), len(lines)):
		playerIndex = int(lines[lineIndex][lines[lineIndex].index("is player ") + len("is player ") : lines[lineIndex].index(" named")])
		users[playerIndex-1]["rank"] = lineIndex - (len(lines) - len(users))
		print("Score of: " + lines[lineIndex][lines[lineIndex].index("score of ") + len("score of ") :])
		users[playerIndex-1]["score"] = float(lines[lineIndex][lines[lineIndex].index("score of ") + len("score of ") :])

	# Update trueskill mu and sigma values
	teams = [[trueskill.Rating(mu=float(user['mu']), sigma=float(user['sigma']))] for user in users]
	newRatings = trueskill.rate(teams)
	for a in range(len(newRatings)):
		users[a]['mu'] = newRatings[a][0].mu
		users[a]['sigma'] = newRatings[a][0].sigma

	backend.gameResult(users, replayPath)

	os.remove(replayPath)

if __name__ == "__main__":
	print("Starting up worker...")
	backend = Backend(1)

	while True:
		task = backend.getTask()
		if task != None:
			print("Got new task: " + str(task))
			if task["type"] == "compile":
				compile(int(task["userID"]), backend)
			elif task["type"] == "game":
				runGame(int(task["width"]), int(task["height"]), task["users"], backend)
			else:
				print("Unknown task")
		else:
			print("No task available. Sleeping for 2 seconds")
			sleep(2)
