#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <cstdlib>
#include <ctime>
#include <stdio.h>
#include <time.h>
#include <set>
#include <fstream>
#include <unistd.h>

#include "hlt.hpp"
#include "Networking.hpp"

int main2(int argc, const char ** argv) { //Ignore as main until needed.

	char * path = new char[FILENAME_MAX];
	getcwd(path, sizeof(char) * FILENAME_MAX);
	strcat(path, "/");
	strcat(path, argv[0]);
	std::string sPath(path);
	while(sPath.back() != '/') sPath.pop_back();
	sPath.pop_back();

	chdir(sPath.c_str()); //Set working directory

	srand(time(NULL));

	std::cout.sync_with_stdio(0);

	unsigned char my_tag;
	hlt::Map present_map;
	getInit(my_tag, present_map);

	std::string s;
	std::ifstream in("Responses.txt");
	if(!in.is_open()) sendInitResponse(sPath);
	else {
		std::getline(in, s);
		sendInitResponse(s + std::to_string(my_tag));
	}

	while(true) {
		getFrame(present_map);

		std::getline(in, s);

		detail::sendString(s);
	}

	return 0;
}
